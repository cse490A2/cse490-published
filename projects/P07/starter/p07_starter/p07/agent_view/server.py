"""Agent view: a live page that shows what the harness's agents are doing.

    python3 agent_view/server.py                  # http://localhost:8797/
    python3 agent_view/server.py 9000             # another port
    python3 agent_view/server.py 8797 path/to/dir # a folder holding trace.jsonl

It reads the trace.jsonl the harness writes, and any other .jsonl file beside
it. Without a folder argument it uses the first of these that holds one:
the folder you run it from, then a harness folder beside this project.

Standard library only. It listens on this computer alone and writes nothing.

Endpoints:
    /                           the page (agent_view.html)
    /api/files                  the .jsonl files in the trace folder, with sizes
    /api/read?file=F&offset=N   the bytes of F from offset N, for live tailing
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
PAGE = HERE / "agent_view.html"
DEFAULT_PORT = 8797
MAX_CHUNK = 4 * 1024 * 1024  # bytes sent per read; the page asks again for more


def trace_folder(argument: str | None) -> Path:
    """Return the folder to read traces from."""
    if argument:
        return Path(argument).resolve()
    candidates = [Path.cwd(), HERE.parent.parent / "harness", HERE.parent]
    for folder in candidates:
        if any(folder.glob("*.jsonl")):
            return folder.resolve()
    return Path.cwd().resolve()


def whole_number(text: str, fallback: int) -> int:
    """Return text as a number that is zero or more, or the fallback."""
    try:
        return max(0, int(text))
    except ValueError:
        return fallback


class Handler(BaseHTTPRequestHandler):
    """Serve the page and the two read-only trace endpoints."""

    folder: Path = Path.cwd()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Stay quiet: the page asks for new lines every second."""

    def reply(self, body: bytes, kind: str, extra: dict | None = None) -> None:
        """Send a 200 with a body that is never cached."""
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802  (the name http.server calls)
        """Route one request."""
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path in ("/", "/index.html", "/agent_view.html"):
            self.reply(PAGE.read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif url.path == "/api/files":
            self.reply(json.dumps(self.files()).encode(), "application/json")
        elif url.path == "/api/read":
            self.read(query)
        else:
            self.send_error(404)

    def files(self) -> dict:
        """List the .jsonl files in the trace folder."""
        listing: dict = {"dir": str(self.folder), "files": []}
        if not self.folder.is_dir():
            listing["error"] = "that folder does not exist"
            return listing
        for path in sorted(self.folder.glob("*.jsonl")):
            if path.is_file():
                listing["files"].append(
                    {"name": path.name, "size": path.stat().st_size}
                )
        return listing

    def read(self, query: dict) -> None:
        """Send one file's bytes from an offset. A name never leaves the folder."""
        name = Path(query.get("file", [""])[0]).name
        path = self.folder / name
        if not name.endswith(".jsonl") or not path.is_file():
            self.send_error(404)
            return
        size = path.stat().st_size
        offset = whole_number(query.get("offset", ["0"])[0], 0)
        if offset > size:  # the file was replaced by a shorter one: start over
            offset = 0
        with path.open("rb") as file:
            file.seek(offset)
            data = file.read(MAX_CHUNK)
        headers = {"X-Offset": str(offset), "X-Size": str(size)}
        self.reply(data, "application/octet-stream", headers)


def main() -> None:
    """Start the server and say where it is."""
    arguments = sys.argv[1:]
    port = whole_number(arguments[0], DEFAULT_PORT) if arguments else DEFAULT_PORT
    Handler.folder = trace_folder(arguments[1] if len(arguments) > 1 else None)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as error:
        sys.exit(f"port {port} is not free ({error}). Try: server.py {port + 1}")
    print(f"Agent view: http://localhost:{port}/", flush=True)
    print(f"Reading traces in: {Handler.folder}", flush=True)
    print("Ctrl+C stops it.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
