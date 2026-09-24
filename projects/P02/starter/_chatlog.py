#!/usr/bin/env python3
"""Course chat log server: one local collector for every AI conversation
this project produces.

Runs as a small HTTP server on 127.0.0.1 (never on the network) because
you said yes during setup; the wizard registered it as a login item so it
is simply always on. Everything it collects lands in _chatlog.jsonl right
here, with a readable _chatlog.md beside it, so you always see exactly
what is recorded. To stop for good, delete this file: the login item only
keeps it running while the file exists, and the wizard's next run asks
again.

Which inlets are on is a per-project decision, declared in _chatlog.json
(written by the setup wizard from the project's pack):

  api      a proxy for the course gateway. Tools that speak the OpenAI or
           Anthropic API (the harness, the VS Code chat extension, Claude
           Code) are pointed at http://127.0.0.1:<port> instead of the
           gateway; every request and reply passes through and is logged.
  browser  web chats with no file and no API (chatgpt.com, claude.ai,
           gemini, lovable). The home page serves one bookmarklet; clicking
           it on a chat page pulls that conversation and shows it here for
           you to save or discard.
  files    tools that keep their own transcript on disk (VS Code chat's
           session store, Claude Code's project transcripts). Polled and
           folded into the same log.

Usage:  python3 _chatlog.py            serve (the normal way; idempotent -
                                       a second start for the same project
                                       exits 0 when one is already up)
        python3 _chatlog.py --once     sweep the file readers once and exit
        python3 _chatlog.py --status   print the running server's health
Flags:  --port N  --inlets api,browser,files  --upstream URL  --config PATH
Stdlib only, Python 3.9+.
"""

import hashlib
import http.client
import json
import os
import re
import ssl
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "1.1"
LOG = "_chatlog.jsonl"          # canonical, machine-read (the characterizer)
VIEW = "_chatlog.md"            # derived, human-readable
STATE = ".chatlog.state.json"   # dedupe keys
CONFIG = "_chatlog.json"
POLL_SECONDS = 20

DEFAULT_CONFIG = {
    "project": "",
    "port": 4400,
    "upstream": "https://litellm-test.cs.washington.edu",
    "inlets": {
        "api": {"clients": ["env", "vscode-chat"]},
        "browser": {"sites": ["chatgpt", "claude", "gemini", "lovable"]},
        "files": {"readers": ["vscode-chat", "claude-code"]},
    },
}


# ------------------------------------------------------------- config

def load_config(argv):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    path = CONFIG
    for a in argv:
        if a.startswith("--config="):
            path = a.split("=", 1)[1]
    if os.path.exists(path):
        try:
            user = json.load(open(path, encoding="utf-8"))
        except ValueError as e:
            sys.exit("%s is not valid JSON: %s" % (path, e))
        for k, v in user.items():
            cfg[k] = v
    if not cfg.get("project"):
        cfg["project"] = os.path.basename(os.getcwd())
    for a in argv:
        if a.startswith("--port="):
            cfg["port"] = int(a.split("=", 1)[1])
        elif a.startswith("--upstream="):
            cfg["upstream"] = a.split("=", 1)[1]
        elif a.startswith("--inlets="):
            names = [n for n in a.split("=", 1)[1].split(",") if n]
            full = json.loads(json.dumps(DEFAULT_CONFIG["inlets"]))
            cfg["inlets"] = {n: cfg.get("inlets", {}).get(n) or full[n] for n in names}
    cfg["upstream"] = cfg["upstream"].rstrip("/")
    return cfg


def inlet_on(cfg, name):
    return isinstance(cfg.get("inlets", {}).get(name), dict)


# -------------------------------------------------------------- store

def text_of(content):
    """Message text from a string or a list of typed parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for p in content:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                if isinstance(p.get("text"), str):
                    out.append(p["text"])
                elif isinstance(p.get("value"), str):
                    out.append(p["value"])
        return "\n".join(s for s in out if s)
    return ""


def sha(*parts):
    return hashlib.sha1("\x1f".join(parts).encode("utf-8", "replace")).hexdigest()


class Store:
    """Append-only records, deduped by key, with the readable mirror."""

    def __init__(self):
        self.lock = threading.Lock()
        try:
            self.seen = set(json.load(open(STATE, encoding="utf-8")))
        except Exception:
            self.seen = set()
        if not os.path.exists(VIEW):
            with open(VIEW, "w", encoding="utf-8") as f:
                f.write("# Chat log\n\nA readable view of _chatlog.jsonl - the "
                        "machine-read record of this project's AI conversations, "
                        "collected because you enabled it during setup.\n\n")

    def count(self):
        try:
            return sum(1 for _ in open(LOG, encoding="utf-8"))
        except OSError:
            return 0

    def add(self, rec, key):
        with self.lock:
            if key in self.seen:
                return False
            self.seen.add(key)
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if rec.get("type") == "turn":
                self._view(rec)
            try:
                json.dump(sorted(self.seen), open(STATE, "w", encoding="utf-8"))
            except OSError:
                pass
            return True

    def session(self, source, session, raw):
        rec = {"v": 2, "type": "session", "source": source, "session": session,
               "raw": raw}
        return self.add(rec, "session:" + session)

    def turn(self, source, session, user, ai, **more):
        rec = {"v": 2, "type": "turn", "source": source, "session": session,
               "request_id": more.pop("request_id", "") or "",
               "ts": more.pop("ts", None) or int(time.time() * 1000),
               "model": more.pop("model", "") or "",
               "mode": more.pop("mode", "") or "",
               "prompt_tokens": more.pop("prompt_tokens", None),
               "completion_tokens": more.pop("completion_tokens", None),
               "elapsed_ms": more.pop("elapsed_ms", None),
               "user": user, "ai": ai,
               "refs": more.pop("refs", []) or [],
               "error": more.pop("error", None),
               "raw": more.pop("raw", None)}
        key = more.pop("key", None) or sha(session, user, ai)
        rec.update(more)
        if ai:
            key += ":done"
        if not user.strip():
            return False
        return self.add(rec, key)

    def _view(self, rec):
        ts = rec.get("ts")
        stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts / 1000)) \
            if ts else time.strftime("%Y-%m-%d %H:%M")
        bits = ["via " + rec.get("source", "?")]
        if rec.get("model"):
            bits.append("model: %s" % rec["model"])
        if rec.get("prompt_tokens") is not None:
            bits.append("tokens: %s in / %s out" % (rec["prompt_tokens"],
                                                    rec.get("completion_tokens", "?")))
        if rec.get("elapsed_ms") is not None:
            bits.append("%.1fs" % (rec["elapsed_ms"] / 1000.0))
        if rec.get("error"):
            bits.append("error: %s" % rec["error"])
        with open(VIEW, "a", encoding="utf-8") as f:
            f.write("## %s (session %s)\n" % (stamp, (rec.get("session") or "")[:8]))
            f.write("*%s*\n" % " - ".join(bits))
            f.write("\n**You:** %s\n\n**AI:** %s\n\n"
                    % (rec["user"], rec["ai"] or "(no text reply)"))


# ---------------------------------------------------------- api inlet

def strip_headers(headers):
    return {k: v for k, v in headers.items()
            if k.lower() not in ("authorization", "x-api-key", "cookie")}


def client_tag(headers):
    tag = headers.get("X-Chatlog-Client")
    if tag:
        return re.sub(r"[^a-z0-9._-]", "", tag.lower())[:32] or "unknown"
    ua = (headers.get("User-Agent") or "").lower()
    if "python" in ua or "openai-python" in ua:
        return "harness"
    if "anthropic" in ua or "claude" in ua:
        return "claude-code"
    if "node" in ua or "undici" in ua or "vscode" in ua or "electron" in ua:
        return "vscode-chat"
    return "unknown" if ua else "vscode-chat"


def parse_request_chat(body):
    """(session, last user text, model, system) from an OpenAI or Anthropic
    chat request body; None when it is not a chat call."""
    try:
        req = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    if not isinstance(req, dict) or not isinstance(req.get("messages"), list):
        return None
    msgs = [m for m in req["messages"] if isinstance(m, dict)]
    users = [text_of(m.get("content")) for m in msgs if m.get("role") == "user"]
    if not users:
        return None
    system = text_of(req.get("system")) if req.get("system") else \
        "\n".join(text_of(m.get("content")) for m in msgs if m.get("role") == "system")
    session = sha(str(req.get("model", "")), system, users[0])[:16]
    return {"session": session, "user": users[-1], "model": str(req.get("model", "")),
            "system": system, "stream": bool(req.get("stream")), "request": req}


def parse_response_text(ctype, body):
    """Assistant text plus usage from a non-streaming JSON reply or an SSE
    stream (OpenAI chat.completions or Anthropic messages)."""
    text, usage, model = [], {}, ""
    data = body.decode("utf-8", "replace")
    if "text/event-stream" in (ctype or "") or data.lstrip().startswith(("data:", "event:")):
        for line in data.splitlines():
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                ev = json.loads(payload)
            except ValueError:
                continue
            for ch in ev.get("choices") or []:
                d = (ch.get("delta") or {}).get("content")
                if isinstance(d, str):
                    text.append(d)
            if ev.get("type") == "content_block_delta":
                d = (ev.get("delta") or {}).get("text")
                if isinstance(d, str):
                    text.append(d)
            if ev.get("type") == "message_start":
                model = (ev.get("message") or {}).get("model", "") or model
                usage = (ev.get("message") or {}).get("usage") or usage
            if ev.get("usage"):
                usage = ev["usage"]
            model = ev.get("model") or model
        return "".join(text), usage, model
    try:
        obj = json.loads(data)
    except ValueError:
        return "", {}, ""
    if not isinstance(obj, dict):
        return "", {}, ""
    for ch in obj.get("choices") or []:
        msg = ch.get("message") or {}
        if isinstance(msg.get("content"), str):
            text.append(msg["content"])
    if isinstance(obj.get("content"), list):
        text.append(text_of(obj["content"]))
    return "".join(text), obj.get("usage") or {}, obj.get("model", "")


def dechunk(rfile):
    out = b""
    while True:
        line = rfile.readline().strip()
        if not line:
            continue
        size = int(line.split(b";")[0], 16)
        if size == 0:
            while rfile.readline().strip():
                pass
            return out
        out += rfile.read(size)
        rfile.readline()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "chatlog/" + VERSION
    cfg = None
    store = None

    def log_message(self, fmt, *args):
        if os.environ.get("CHATLOG_DEBUG"):
            sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    # -- routing -------------------------------------------------------
    def _local_host(self):
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        return host in ("127.0.0.1", "localhost", "::1")

    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch()

    def do_OPTIONS(self):
        self.dispatch()

    def do_PUT(self):
        self.dispatch()

    def do_DELETE(self):
        self.dispatch()

    def dispatch(self):
        if not self._local_host():
            return self.send_text(403, "local only\n")
        path = urllib.parse.urlparse(self.path).path
        if path == "/" or path == "/index.html":
            return self.page_home()
        if path == "/_/health":
            return self.send_json(200, self.health())
        if path == "/_/bookmarklet":
            return self.send_text(200, bookmarklet_js(self.cfg), "text/plain; charset=utf-8")
        if path == "/_/ingest":
            if not inlet_on(self.cfg, "browser"):
                return self.send_text(404, "the browser inlet is off for this project\n")
            if self.command == "POST":
                return self.ingest()
            return self.page_ingest()
        if path == "/_/recent":
            return self.send_json(200, {"records": recent_records(12)})
        if inlet_on(self.cfg, "api"):
            if self.command == "GET" and path in ("/v1/model/info", "/model/info"):
                return self.model_info()
            return self.proxy()
        self.send_text(404, "the api inlet is off for this project\n")

    def health(self):
        return {"ok": True, "project": self.cfg["project"], "port": self.cfg["port"],
                "version": VERSION, "pid": os.getpid(), "inlets": sorted(self.cfg.get("inlets", {})),
                "upstream": self.cfg["upstream"] if inlet_on(self.cfg, "api") else None,
                "records": self.store.count(), "cwd": os.getcwd()}

    # -- replies -------------------------------------------------------
    def send_text(self, code, text, ctype="text/plain; charset=utf-8"):
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def send_json(self, code, obj):
        self.send_text(code, json.dumps(obj, ensure_ascii=False, indent=1) + "\n",
                       "application/json; charset=utf-8")

    def read_body(self):
        if (self.headers.get("Transfer-Encoding") or "").lower() == "chunked":
            return dechunk(self.rfile)
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    # -- model info ----------------------------------------------------
    def upstream_get(self, path):
        """GET one upstream path with the caller's credentials. Returns
        (status, parsed json or None)."""
        up = urllib.parse.urlparse(self.cfg["upstream"])
        conn_cls = http.client.HTTPSConnection if up.scheme == "https" else http.client.HTTPConnection
        kw = {"timeout": 30}
        if up.scheme == "https":
            kw["context"] = ssl.create_default_context()
        headers = {"Host": up.netloc, "Accept-Encoding": "identity", "Connection": "close"}
        for k in ("Authorization", "x-api-key"):
            v = self.headers.get(k)
            if v:
                headers[k] = v
        conn = conn_cls(up.hostname, up.port, **kw)
        conn.request("GET", (up.path or "") + path, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        try:
            return resp.status, json.loads(data.decode("utf-8"))
        except ValueError:
            return resp.status, None

    def model_info(self):
        """The VS Code chat extension discovers models from /v1/model/info
        and never looks at /v1/models when that answers. On the course
        gateway a student key sees only the locally hosted deployments
        there, most of them flagged blocked, while /v1/models lists every
        model the key can actually call (16 against 1 on 2026-09-16). So
        the picker showed one model. Until the gateway lists them itself,
        this answers with the gateway's unblocked entries plus one plain
        chat entry per model that /v1/models names and model/info does
        not. Any upstream trouble falls through to the byte-for-byte
        proxy, so nothing here can make the extension worse off."""
        try:
            st_info, info = self.upstream_get("/v1/model/info")
            st_models, models = self.upstream_get("/v1/models")
        except Exception:
            return self.proxy()
        if st_info != 200 or st_models != 200 or not isinstance(info, dict) \
                or not isinstance(models, dict):
            return self.proxy()
        entries = [e for e in info.get("data") or [] if isinstance(e, dict)
                   and not (e.get("model_info") or {}).get("blocked")]
        seen = set(e.get("model_name") for e in entries)
        for m in models.get("data") or []:
            mid = m.get("id") if isinstance(m, dict) else None
            if mid and mid not in seen:
                seen.add(mid)
                entries.append({"model_name": mid,
                                "litellm_params": {"model": mid},
                                "model_info": {"id": mid, "mode": "chat",
                                               "listed_by": "chatlog from /v1/models"}})
        self.send_json(200, {"data": entries})

    # -- the proxy -----------------------------------------------------
    def proxy(self):
        body = self.read_body()
        up = urllib.parse.urlparse(self.cfg["upstream"])
        conn_cls = http.client.HTTPSConnection if up.scheme == "https" else http.client.HTTPConnection
        kw = {"timeout": 600}
        if up.scheme == "https":
            kw["context"] = ssl.create_default_context()
        conn = conn_cls(up.hostname, up.port, **kw)
        headers = {}
        for k, v in self.headers.items():
            if k.lower() in ("host", "connection", "keep-alive", "transfer-encoding",
                             "content-length", "accept-encoding"):
                continue
            headers[k] = v
        headers["Host"] = up.netloc
        headers["Accept-Encoding"] = "identity"
        headers["Connection"] = "close"
        if body:
            headers["Content-Length"] = str(len(body))
        t0 = time.time()
        chat = parse_request_chat(body) if body else None
        try:
            conn.request(self.command, (up.path or "") + self.path, body=body or None,
                         headers=headers)
            resp = conn.getresponse()
        except Exception as e:
            self.send_json(502, {"error": {"message": "chat log server could not reach "
                                            "%s: %r" % (self.cfg["upstream"], e)}})
            if chat:
                self.record_turn(chat, 502, "", b"", t0, error="upstream unreachable: %r" % e)
            return
        self.send_response(resp.status, resp.reason)
        ctype = resp.getheader("Content-Type", "")
        length = resp.getheader("Content-Length")
        chunked = length is None
        for k, v in resp.getheaders():
            if k.lower() in ("connection", "keep-alive", "transfer-encoding",
                             "content-length", "content-encoding"):
                continue
            self.send_header(k, v)
        if chunked:
            self.send_header("Transfer-Encoding", "chunked")
        else:
            self.send_header("Content-Length", length)
        self.send_header("Connection", "close")
        self.end_headers()
        collected = []
        try:
            while True:
                piece = resp.read(4096)
                if not piece:
                    break
                collected.append(piece)
                if chunked:
                    self.wfile.write(b"%x\r\n%s\r\n" % (len(piece), piece))
                else:
                    self.wfile.write(piece)
                self.wfile.flush()
            if chunked:
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            conn.close()
            self.close_connection = True
        if chat:
            self.record_turn(chat, resp.status, ctype, b"".join(collected), t0)

    def record_turn(self, chat, status, ctype, raw, t0, error=None):
        ai, usage, model = parse_response_text(ctype, raw) if raw else ("", {}, "")
        if status >= 400 and not error:
            error = "HTTP %d %s" % (status, raw.decode("utf-8", "replace")[:160].strip())
        source = "api:" + client_tag(self.headers)
        self.store.session(source, chat["session"],
                           {"model": chat["model"], "system": chat["system"][:2000],
                            "path": self.path, "client": source})
        raw_resp = raw.decode("utf-8", "replace")
        try:
            raw_resp = json.loads(raw_resp)
        except ValueError:
            pass
        rid = sha(chat["session"], str(t0), str(id(self)))[:16]
        self.store.turn(
            source, chat["session"], chat["user"], ai, key="api:" + rid,
            request_id=rid,
            ts=int(t0 * 1000), model=model or chat["model"],
            mode="stream" if chat["stream"] else "",
            prompt_tokens=usage.get("prompt_tokens", usage.get("input_tokens")),
            completion_tokens=usage.get("completion_tokens", usage.get("output_tokens")),
            elapsed_ms=int((time.time() - t0) * 1000), error=error,
            raw={"request": {"path": self.path, "headers": strip_headers(dict(self.headers)),
                             "body": chat["request"]},
                 "response": {"status": status, "content_type": ctype, "body": raw_resp}})

    # -- the browser inlet ---------------------------------------------
    def ingest(self):
        try:
            payload = json.loads(self.read_body().decode("utf-8"))
        except Exception:
            return self.send_json(400, {"error": "not JSON"})
        n = ingest_conversation(self.store, payload)
        self.send_json(200, {"saved": n, "records": self.store.count()})

    def page_home(self):
        self.send_text(200, home_html(self.cfg, self.store), "text/html; charset=utf-8")

    def page_ingest(self):
        self.send_text(200, ingest_html(self.cfg), "text/html; charset=utf-8")


def ingest_conversation(store, payload):
    """A conversation the bookmarklet collected: {site, id, url, title,
    fidelity, messages: [{role, text, ts?, model?}], raw?}."""
    if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
        return 0
    site = re.sub(r"[^a-z0-9.-]", "", str(payload.get("site", "web")).lower()) or "web"
    cid = str(payload.get("id") or sha(str(payload.get("url", "")))[:12])
    session = "%s:%s" % (site, cid)
    source = "browser:" + site
    store.session(source, session, {"url": payload.get("url"), "title": payload.get("title"),
                                    "fidelity": payload.get("fidelity"),
                                    "collected": int(time.time() * 1000)})
    saved, pending = 0, None
    msgs = [m for m in payload["messages"] if isinstance(m, dict)]
    for i, m in enumerate(msgs):
        role, text = m.get("role"), str(m.get("text") or "")
        if role == "user":
            if pending is not None:
                saved += store.turn(source, session, pending["text"], "",
                                    key=sha(session, str(pending["i"]), pending["text"]),
                                    ts=pending.get("ts"), model=pending.get("model", ""),
                                    raw={"index": pending["i"], "message": pending["m"]})
            pending = {"i": i, "text": text, "ts": m.get("ts"), "model": m.get("model", ""), "m": m}
        elif role == "assistant" and pending is not None:
            saved += store.turn(source, session, pending["text"], text,
                                key=sha(session, str(pending["i"]), pending["text"], text),
                                ts=pending.get("ts") or m.get("ts"),
                                model=m.get("model") or pending.get("model", ""),
                                raw={"index": pending["i"], "user": pending["m"], "assistant": m})
            pending = None
    if pending is not None:
        saved += store.turn(source, session, pending["text"], "",
                            key=sha(session, str(pending["i"]), pending["text"]),
                            ts=pending.get("ts"), model=pending.get("model", ""),
                            raw={"index": pending["i"], "message": pending["m"]})
    return saved


def recent_records(n):
    try:
        lines = open(LOG, encoding="utf-8").read().splitlines()
    except OSError:
        return []
    out = []
    for line in reversed(lines):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") != "turn":
            continue
        out.append({"ts": r.get("ts"), "source": r.get("source"), "model": r.get("model"),
                    "user": (r.get("user") or "")[:160], "ai": (r.get("ai") or "")[:160]})
        if len(out) >= n:
            break
    return out


# Per-site adapters run inside the chat page with its own login session.
# api = the site's own conversation endpoint (full fidelity); dom = the
# messages as rendered; page = the visible text as one message.
SITE_ADAPTERS = {
    "chatgpt": r"""
if(/(^|\.)chatgpt\.com$|(^|\.)openai\.com$/.test(h)){site='chatgpt';
 var m=location.pathname.match(/\/c\/([0-9a-f-]{36})/);if(!m)throw 'Open a conversation first (the address should contain /c/...)';
 var s=await(await fetch('/api/auth/session',{credentials:'include'})).json();
 var r=await fetch('/backend-api/conversation/'+m[1],{headers:{Authorization:'Bearer '+s.accessToken},credentials:'include'});
 if(!r.ok)throw 'chatgpt api answered '+r.status;var c=await r.json();var chain=[],n=c.current_node;
 while(n&&c.mapping[n]){chain.unshift(c.mapping[n]);n=c.mapping[n].parent}
 for(var x of chain){var g=x.message;if(!g||!g.author)continue;var role=g.author.role;if(role!=='user'&&role!=='assistant')continue;
  var parts=((g.content&&g.content.parts)||[]).filter(function(p){return typeof p==='string'}).join('\n');if(!parts.trim())continue;
  out.push({role:role,text:parts,ts:g.create_time?Math.round(g.create_time*1000):null,model:(g.metadata&&g.metadata.model_slug)||''})}
 return {site:site,id:m[1],title:c.title||document.title,fidelity:'api',messages:out,raw:{title:c.title,create_time:c.create_time,update_time:c.update_time}}}
""",
    "claude": r"""
if(/(^|\.)claude\.ai$/.test(h)){site='claude';
 var m=location.pathname.match(/\/chat\/([0-9a-f-]{36})/);if(!m)throw 'Open a conversation first (the address should contain /chat/...)';
 var orgs=await(await fetch('/api/organizations',{credentials:'include'})).json();var org=null;
 for(var o of orgs){if(!org||(o.capabilities||[]).indexOf('chat')>=0)org=o.uuid}
 var r=await fetch('/api/organizations/'+org+'/chat_conversations/'+m[1]+'?tree=True&rendering_mode=messages&render_all_tools=true',{credentials:'include'});
 if(!r.ok)throw 'claude api answered '+r.status;var c=await r.json();
 for(var g of (c.chat_messages||[])){var role=g.sender==='human'?'user':(g.sender==='assistant'?'assistant':null);if(!role)continue;
  var t=(g.content||[]).filter(function(b){return b.type==='text'&&b.text}).map(function(b){return b.text}).join('\n');if(!t.trim()&&g.text)t=g.text;if(!t.trim())continue;
  out.push({role:role,text:t,ts:g.created_at?Date.parse(g.created_at):null,model:c.model||''})}
 return {site:site,id:m[1],title:c.name||document.title,fidelity:'api',messages:out,raw:{name:c.name,model:c.model,created_at:c.created_at,updated_at:c.updated_at}}}
""",
    "gemini": r"""
if(/(^|\.)gemini\.google\.com$/.test(h)){site='gemini';
 var els=document.querySelectorAll('user-query, model-response');
 for(var e of els){var role=e.tagName.toLowerCase()==='user-query'?'user':'assistant';var t=(e.innerText||'').trim();if(t)out.push({role:role,text:t})}
 if(!out.length)throw 'No messages found on this page';
 return {site:site,id:(location.pathname.match(/\/app\/([0-9a-f]+)/)||[])[1]||'',title:document.title,fidelity:'dom',messages:out}}
""",
    "lovable": r"""
if(/(^|\.)lovable\.(dev|app)$/.test(h)){site='lovable';
 var els=document.querySelectorAll('[data-message-role],[data-role="user"],[data-role="assistant"]');
 for(var e of els){var role=(e.getAttribute('data-message-role')||e.getAttribute('data-role')||'').toLowerCase();role=role==='user'?'user':(role?'assistant':null);var t=(e.innerText||'').trim();if(role&&t)out.push({role:role,text:t})}
 if(!out.length){var t2=(document.body.innerText||'').trim();if(!t2)throw 'No text found on this page';out.push({role:'user',text:t2});
  return {site:site,id:(location.pathname.match(/\/projects\/([0-9a-f-]+)/)||[])[1]||'',title:document.title,fidelity:'page',messages:out}}
 return {site:site,id:(location.pathname.match(/\/projects\/([0-9a-f-]+)/)||[])[1]||'',title:document.title,fidelity:'dom',messages:out}}
""",
}

BOOKMARKLET = r"""(async function(){var P='__BASE__';var h=location.hostname,site='',out=[],payload=null,err=null;
try{payload=await (async function(){
__ADAPTERS__
throw 'No adapter for '+h+' - this project logs: __SITES__'})()}catch(e){err=e}
function open2(frag){var w=window.open(P+'/_/ingest#'+frag,'chatlog');if(!w)alert('Allow pop-ups for this site (the icon at the right of the address bar), then click the bookmark again.');return w}
if(err){open2(encodeURIComponent(JSON.stringify({chatlog:'error',url:location.href,message:String(err)})));return}
payload.url=location.href;payload.collected=Date.now();var data=JSON.stringify({chatlog:'conversation',conversation:payload});
if(data.length<1500000){open2(encodeURIComponent(data));return}
var w=open2('');if(!w)return;window.addEventListener('message',function(ev){if(ev.origin===P&&ev.data&&ev.data.chatlog==='ready')w.postMessage({chatlog:'conversation',conversation:payload},P)});
})();"""


def bookmarklet_js(cfg):
    sites = (cfg.get("inlets", {}).get("browser") or {}).get("sites") or []
    adapters = "\n".join(SITE_ADAPTERS[s].strip() for s in sites if s in SITE_ADAPTERS)
    base = "http://127.0.0.1:%d" % cfg["port"]
    js = BOOKMARKLET.replace("__BASE__", base).replace("__ADAPTERS__", adapters) \
        .replace("__SITES__", ", ".join(sites))
    js = " ".join(line.strip() for line in js.splitlines() if line.strip())
    return "javascript:" + urllib.parse.quote(js, safe="()[]{}:;,.=+-*/<>!&|'\"?_$ ")


def adapters_note(cfg):
    sites = (cfg.get("inlets", {}).get("browser") or {}).get("sites") or []
    return ", ".join(sites)


CSS = """
body{font:15px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0;background:#f7f5ef;color:#222}
main{max-width:760px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:26px 0 8px}
.card{background:#fff;border:1px solid #ddd6c4;border-radius:8px;padding:14px 16px;margin:10px 0}
.k{color:#6b6357}.ok{color:#2a7a3b}.bad{color:#a83232}
a.bm{display:inline-block;background:#4b3f8f;color:#fff;padding:9px 14px;border-radius:6px;text-decoration:none;font-weight:600;cursor:grab}
button{font:inherit;padding:8px 14px;border-radius:6px;border:1px solid #bbb;background:#fff;cursor:pointer}
button.p{background:#2a7a3b;color:#fff;border-color:#2a7a3b}
.msg{padding:8px 10px;border-radius:6px;margin:6px 0;white-space:pre-wrap;word-break:break-word}
.user{background:#eef1fb}.assistant{background:#f2f7f0}
.tiny{font-size:12px;color:#6b6357}
code{background:#eee;padding:1px 4px;border-radius:3px}
"""


def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def home_html(cfg, store):
    inlets = cfg.get("inlets", {})
    rows = []
    if inlet_on(cfg, "api"):
        rows.append("<div class=card><b>API proxy</b> <span class=ok>on</span><br>"
                    "<span class=k>Tools pointed at <code>http://127.0.0.1:%d</code> reach "
                    "<code>%s</code> through this server; every call is logged.</span></div>"
                    % (cfg["port"], html_escape(cfg["upstream"])))
    if inlet_on(cfg, "browser"):
        rows.append("<div class=card><b>Web chats</b> <span class=ok>on</span> "
                    "<span class=k>(%s)</span><br>"
                    "<p>Drag this button to your bookmarks bar once. Then, on a chat page, "
                    "click it: the conversation opens here for you to save or discard.</p>"
                    "<a class=bm href=\"%s\">Log this chat</a> "
                    "<span class=tiny>bookmarklet v%s</span></div>"
                    % (html_escape(adapters_note(cfg)), html_escape(bookmarklet_js(cfg)), VERSION))
    if inlet_on(cfg, "files"):
        readers = ", ".join((inlets.get("files") or {}).get("readers") or [])
        rows.append("<div class=card><b>Transcript files</b> <span class=ok>on</span> "
                    "<span class=k>(%s)</span><br><span class=k>Read from those tools' own "
                    "session stores every %d seconds.</span></div>" % (html_escape(readers), POLL_SECONDS))
    recent = "".join(
        "<div class=card><div class=tiny>%s - %s%s</div><div class='msg user'>%s</div>"
        "<div class='msg assistant'>%s</div></div>" % (
            time.strftime("%Y-%m-%d %H:%M", time.localtime((r.get("ts") or 0) / 1000)),
            html_escape(r.get("source")), (" - " + html_escape(r["model"])) if r.get("model") else "",
            html_escape(r.get("user")), html_escape(r.get("ai") or "(no text reply)"))
        for r in recent_records(6)) or "<p class=k>Nothing logged yet.</p>"
    return ("<!doctype html><meta charset=utf-8><title>Chat log - %s</title><style>%s</style>"
            "<main><h1>Chat log for %s</h1><p class=k>Running on 127.0.0.1:%d, this machine only. "
            "%d records in <code>_chatlog.jsonl</code>; the readable copy is <code>_chatlog.md</code>.</p>"
            "%s<h2>Latest</h2>%s</main>"
            % (html_escape(cfg["project"]), CSS, html_escape(cfg["project"]), cfg["port"],
               store.count(), "".join(rows), recent))


def ingest_html(cfg):
    return ("<!doctype html><meta charset=utf-8><title>Save this chat?</title><style>%s</style>"
            "<main><h1>Save this chat?</h1><p id=status class=k>Waiting for the chat page...</p>"
            "<div id=meta class=tiny></div><div id=list></div>"
            "<p id=actions hidden><button class=p id=save>Save to the log</button> "
            "<button id=discard>Discard</button></p></main>"
            "<script>"
            "var conv=null;var S=document.getElementById('status'),L=document.getElementById('list'),"
            "A=document.getElementById('actions'),M=document.getElementById('meta');"
            "function esc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}"
            "function take(d){"
            "if(d.chatlog==='error'){S.textContent='Could not collect it: '+d.message;S.className='bad';return}"
            "if(d.chatlog!=='conversation')return;conv=d.conversation;conv.url=d.url||conv.url;conv.collected=d.collected||conv.collected;"
            "S.textContent=conv.messages.length+' messages from '+conv.site+' ('+conv.fidelity+'). Save them to this project\\'s log?';"
            "M.textContent=(conv.title||'')+' - '+(conv.url||'');"
            "L.innerHTML=conv.messages.map(function(m){return '<div class=\"msg '+m.role+'\">'+esc(m.text)+'</div>'}).join('');"
            "A.hidden=false}"
            "window.addEventListener('message',function(ev){take(ev.data||{})});"
            "if(location.hash.length>1){try{take(JSON.parse(decodeURIComponent(location.hash.slice(1))))}catch(e){S.textContent='Could not read the conversation: '+e;S.className='bad'}}"
            "document.getElementById('save').onclick=function(){fetch('/_/ingest',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(conv)})"
            ".then(function(r){return r.json()}).then(function(j){S.textContent='Saved '+j.saved+' new turn(s). '+j.records+' records in the log now.';S.className='ok';A.hidden=true})"
            ".catch(function(e){S.textContent='Save failed: '+e;S.className='bad'})};"
            "document.getElementById('discard').onclick=function(){window.close();S.textContent='Discarded - nothing written.';A.hidden=true};"
            "if(location.hash.length<=1&&window.opener)window.opener.postMessage({chatlog:'ready'},'*');"
            "</script>" % CSS)


# -------------------------------------------------------- files inlet

def vscode_storage_root():
    override = os.environ.get("CHATWATCH_STORAGE")
    if override:
        return override
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return os.path.join(home, "Library", "Application Support", "Code", "User", "workspaceStorage")
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA", ""), "Code", "User", "workspaceStorage")
    return os.path.join(home, ".config", "Code", "User", "workspaceStorage")


def vscode_session_dirs():
    """The workspaceStorage folders whose workspace is THIS folder."""
    here = os.path.realpath(os.getcwd())
    root = vscode_storage_root()
    out = []
    if not os.path.isdir(root):
        return out
    for entry in os.listdir(root):
        meta = os.path.join(root, entry, "workspace.json")
        try:
            folder = json.load(open(meta, encoding="utf-8")).get("folder", "")
        except Exception:
            continue
        if folder.startswith("file://"):
            path = os.path.realpath(urllib.parse.unquote(urllib.parse.urlparse(folder).path))
            if os.name == "nt" and path.startswith(("\\", "/")):
                path = path.lstrip("/\\")
            if os.path.normcase(path) == os.path.normcase(here):
                out.append(os.path.join(root, entry, "chatSessions"))
    return out


def vscode_replay(lines):
    """Rebuild a VS Code chat session from its delta log.
    kind 0 = snapshot, kind 1 = set at path, kind 2 = append to list."""
    state = {}
    for line in lines:
        try:
            op = json.loads(line)
        except ValueError:
            continue
        kind, path, v = op.get("kind"), op.get("k"), op.get("v")
        if kind == 0:
            state = op.get("v", {}) or {}
            continue
        if not isinstance(path, list) or not path:
            continue
        node = state
        try:
            for key in path[:-1]:
                node = node[key]
            last = path[-1]
            if kind == 1:
                node[last] = v
            elif kind == 2:
                target = node.get(last) if isinstance(node, dict) else node[last]
                if isinstance(target, list) and isinstance(v, list):
                    target.extend(v)
                else:
                    node[last] = list(v) if isinstance(v, list) else v
        except (KeyError, IndexError, TypeError):
            continue
    return state


def vscode_text(response):
    out = []
    if isinstance(response, list):
        for part in response:
            if not isinstance(part, dict) or part.get("kind") == "thinking":
                continue
            if part.get("kind") == "inlineReference":
                ref = part.get("inlineReference") or {}
                name = os.path.basename(ref.get("path") or ref.get("fsPath") or ref.get("name") or "")
                if name and out:
                    out[-1] = out[-1] + "`" + name + "`"
                elif name:
                    out.append("`" + name + "`")
                continue
            v = part.get("value")
            if not isinstance(v, str) or not v.strip():
                continue
            if out and (v.startswith(out[-1]) or out[-1].startswith(v)):
                if len(v) > len(out[-1]):
                    out[-1] = v
            elif v not in out:
                out.append(v)
    return "".join(out)


def read_vscode_chat(store):
    new = 0
    for d in vscode_session_dirs():
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".jsonl"):
                continue
            try:
                lines = open(os.path.join(d, name), encoding="utf-8", errors="replace").read().splitlines()
            except OSError:
                continue
            state = vscode_replay(lines)
            session = state.get("sessionId") or name.split(".")[0]
            meta = {k: v for k, v in state.items() if k not in ("requests", "pendingRequests")}
            new += store.session("files:vscode-chat", session, meta)
            for r in state.get("requests", []) or []:
                if not isinstance(r, dict):
                    continue
                msg = r.get("message")
                if not (isinstance(msg, dict) and isinstance(msg.get("text"), str)):
                    continue
                refs = []
                for part in r.get("response") or []:
                    if isinstance(part, dict) and part.get("kind") == "inlineReference":
                        ref = part.get("inlineReference") or {}
                        n = os.path.basename(ref.get("path") or ref.get("fsPath") or "")
                        if n and n not in refs:
                            refs.append(n)
                err = ((r.get("result") or {}).get("errorDetails") or {}).get("message")
                ai = vscode_text(r.get("response"))
                new += store.turn(
                    "files:vscode-chat", session, msg["text"], ai,
                    key=(r.get("requestId") or sha(session, msg["text"], ai)),
                    request_id=r.get("requestId", ""), ts=r.get("timestamp"),
                    model=r.get("modelId", ""), mode=(r.get("modeInfo") or {}).get("kind", ""),
                    prompt_tokens=r.get("promptTokens"), completion_tokens=r.get("completionTokens"),
                    elapsed_ms=r.get("elapsedMs"), refs=refs,
                    error=(err or "").split("\n")[0][:200] or None, raw=r)
    return new


def claude_code_dirs():
    """Claude Code keeps one folder per project under ~/.claude/projects,
    named from the project path with every non-alphanumeric run as '-'."""
    root = os.environ.get("CHATLOG_CLAUDE_DIR") or os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(root):
        return []
    here = os.path.realpath(os.getcwd())
    slug = re.sub(r"[^A-Za-z0-9]", "-", here)
    out = []
    for entry in os.listdir(root):
        if entry == slug:
            out.append(os.path.join(root, entry))
    return out


def read_claude_code(store):
    """One turn = one typed prompt plus every assistant text until the
    next prompt (tool calls and tool results in between are skipped)."""
    new = 0

    def flush(session, p):
        return store.turn("files:claude-code", session, p["text"], "\n".join(p["ai"]),
                          key=p["uuid"], request_id=p["uuid"], ts=p["ts"],
                          model=p["model"], prompt_tokens=p["in"], completion_tokens=p["out"],
                          raw={"user_uuid": p["uuid"], "assistant_uuids": p["auuids"]})

    for d in claude_code_dirs():
        for name in sorted(os.listdir(d)):
            if not name.endswith(".jsonl"):
                continue
            session = name[:-6]
            pending = None
            try:
                lines = open(os.path.join(d, name), encoding="utf-8", errors="replace")
            except OSError:
                continue
            first = True
            for line in lines:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                typ = ev.get("type")
                msg = ev.get("message") or {}
                if typ not in ("user", "assistant") or not isinstance(msg, dict):
                    continue
                content = msg.get("content")
                if typ == "user" and isinstance(content, list) and any(
                        isinstance(p, dict) and p.get("type") == "tool_result" for p in content):
                    continue
                text = text_of(content)
                if not text.strip() or (typ == "user" and text.lstrip().startswith("<")):
                    continue
                if first:
                    new += store.session("files:claude-code", session,
                                         {"cwd": ev.get("cwd"), "version": ev.get("version")})
                    first = False
                ts = ev.get("timestamp")
                try:
                    ts_ms = int(time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")) * 1000) if ts else None
                except Exception:
                    ts_ms = None
                if typ == "user":
                    if pending:
                        new += flush(session, pending)
                    pending = {"text": text, "uuid": ev.get("uuid") or sha(session, text),
                               "ts": ts_ms, "ai": [], "auuids": [], "model": "", "in": None, "out": None}
                elif pending:
                    pending["ai"].append(text)
                    pending["auuids"].append(ev.get("uuid"))
                    pending["model"] = msg.get("model") or pending["model"]
                    u = msg.get("usage") or {}
                    if u.get("input_tokens") is not None:
                        pending["in"] = u.get("input_tokens")
                        pending["out"] = (pending["out"] or 0) + (u.get("output_tokens") or 0)
            if pending:
                new += flush(session, pending)
    return new


READERS = {"vscode-chat": read_vscode_chat, "claude-code": read_claude_code}


def sweep_files(cfg, store):
    names = (cfg.get("inlets", {}).get("files") or {}).get("readers") or []
    new = 0
    for n in names:
        fn = READERS.get(n)
        if fn:
            try:
                new += fn(store)
            except Exception as e:
                if os.environ.get("CHATLOG_DEBUG"):
                    sys.stderr.write("reader %s: %r\n" % (n, e))
    return new


# --------------------------------------------------------------- main

def running_health(port):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/_/health" % port, timeout=2) as r:
            return json.load(r)
    except Exception:
        return None


def serve(cfg):
    port = cfg["port"]
    Handler.cfg = cfg
    Handler.store = Store()
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError:
        other = running_health(port)
        if other and other.get("project") == cfg["project"]:
            print("chat log server already running for %s on port %d" % (cfg["project"], port))
            return 0
        print("port %d is taken by %s - stop it or pick another port in %s"
              % (port, ("another project: " + other["project"]) if other else "something else", CONFIG))
        return 1
    srv.daemon_threads = True
    if inlet_on(cfg, "files"):
        def loop():
            while True:
                sweep_files(cfg, Handler.store)
                time.sleep(POLL_SECONDS)
        threading.Thread(target=loop, daemon=True).start()
    print("chat log server for %s on http://127.0.0.1:%d  inlets: %s"
          % (cfg["project"], port, ", ".join(sorted(cfg.get("inlets", {})))))
    if sys.stdout:            # None under pythonw
        sys.stdout.flush()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


def main(argv):
    # Files live beside this script whatever the caller's directory (a
    # login item starts us with no useful working directory).
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cfg = load_config(argv)
    if "--status" in argv:
        h = running_health(cfg["port"])
        print(json.dumps(h, indent=1) if h else "not running on port %d" % cfg["port"])
        return 0 if h else 1
    if "--once" in argv:
        n = sweep_files(cfg, Store())
        print("added %d new record(s) to %s" % (n, LOG))
        return 0
    return serve(cfg)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
