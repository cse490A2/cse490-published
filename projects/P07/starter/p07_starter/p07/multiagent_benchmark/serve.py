#!/usr/bin/env python3
"""Serve the frozen pages on http://localhost:8765/ . Standard library only.

    python3 serve.py            # port 8765
    python3 serve.py 9000       # another port; then change 8765 to 9000 in questions.md and job_desc

GET /            an HTML index linking every page, with its group, source URL and fetch date
GET /<file>.txt  the page as text/plain (UTF-8)

Where the pages come from, first match wins:
  1. the directory named by the environment variable P07_PAGES, when set
  2. ../p07-pages/pages, relative to this folder (a p07-pages folder beside the job folder)
  3. ./pages, the pages folder inside this folder
  4. ./pages.zip, unpacked into ./pages the first time
"""
import html, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


def pages_dir():
    candidates = []
    if os.environ.get("P07_PAGES"):
        candidates.append(os.environ["P07_PAGES"])
    candidates.append(os.path.join(os.path.dirname(os.path.dirname(HERE)), "p07-pages", "pages"))
    candidates.append(os.path.join(HERE, "pages"))
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)
    packed = os.path.join(HERE, "pages.zip")
    if os.path.isfile(packed):  # first run: the pages come packed beside this file
        import zipfile
        with zipfile.ZipFile(packed) as archive:
            archive.extractall(HERE)
        print("unpacked pages.zip")
        return os.path.join(HERE, "pages")
    sys.exit("no pages folder found; tried: " + ", ".join(candidates))


PAGES = pages_dir()
DEFAULT_PORT = 8765  # the port questions.md and the job files name
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT


def page_meta(fn):
    """SOURCE, FETCHED and GROUP from the file's header lines."""
    meta = {}
    with open(os.path.join(PAGES, fn), encoding="utf-8") as f:
        for _ in range(4):
            line = f.readline()
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".txt": "text/plain; charset=utf-8",
                      ".md": "text/plain; charset=utf-8"}

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=PAGES, **kw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            files = sorted(f for f in os.listdir(PAGES) if f.endswith(".txt"))
            rows = []
            for fn in files:
                m = page_meta(fn)
                rows.append(f'<tr><td><a href="/{fn}">{html.escape(fn)}</a></td>'
                            f'<td>{html.escape(m.get("GROUP", ""))}</td>'
                            f'<td>{html.escape(m.get("SOURCE", ""))}</td>'
                            f'<td>{html.escape(m.get("FETCHED", ""))}</td></tr>')
            body = ("<!doctype html><meta charset=utf-8><title>P07 pages</title>"
                    "<h1>Frozen pages</h1><p>Each page is plain text. "
                    "Name the filename with every answer.</p>"
                    "<table border=1 cellpadding=4><tr><th>file</th><th>group</th><th>source</th><th>fetched</th></tr>"
                    + "".join(rows) + "</table>").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


def port_in_use():
    """Say plainly why the port is taken, and what to do. Then stop."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=3) as reply:
            ours = b"<title>P07 pages</title>" in reply.read(400)
    except OSError:
        ours = False
    if ours:
        sys.exit(f"The page server is already running at http://localhost:{PORT}/ "
                 "(in another terminal). You do not need to start it again.")
    import subprocess
    try:  # name the program that holds the port, when the system can say
        pid = subprocess.run(["lsof", "-ti", f"tcp:{PORT}", "-sTCP:LISTEN"],
                             capture_output=True, text=True).stdout.split()[0]
        what = subprocess.run(["ps", "-p", pid, "-o", "command="],
                              capture_output=True, text=True).stdout.strip()
    except (OSError, IndexError):
        pid, what = "", ""
    if "serve.py" in what:
        sys.exit(f"An old page server (process {pid}) holds port {PORT} and does not answer.\n"
                 f"Stop it:  kill {pid}\n"
                 "Then run serve.py again.")
    sys.exit(f"Another program is using port {PORT}, and it is not the page server.\n"
             + (f"It is process {pid}: {what[:80]}\n" if pid else f"See what it is:  lsof -i :{PORT}\n")
             + "Close that program and run serve.py again. Keep this port: "
             "questions.md and the job files name it.")


if __name__ == "__main__":
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        port_in_use()
    with srv:
        print(f"serving {PAGES} at http://localhost:{PORT}/  (Ctrl-C to stop)")
        if PORT != DEFAULT_PORT:
            print(f"NOTE: questions.md and the job files name port {DEFAULT_PORT}, so the team "
                  f"will not find these pages.\nIn your harness folder, change {DEFAULT_PORT} "
                  f"to {PORT} in questions.md and in each file in job_desc before you run a job.")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
