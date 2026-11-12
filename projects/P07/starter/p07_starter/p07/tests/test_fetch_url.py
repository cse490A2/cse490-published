"""Test for fetch_url: a page comes back as plain text, cut at 8,000 characters.

The page is served from this machine, so the test needs no network.
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from toolcheck import check, is_error, tool

PAGE = (
    "<html><head><title>Harbor</title>"
    "<style>body { color: crimson; }</style>"
    "<script>var hidden = 'secretvalue';</script></head>"
    "<body><h1>Lighthouse</h1><p>The lamp turns <b>twice</b> a minute.</p>"
    + "<p>filler words</p>" * 2000
    + "</body></html>"
)


class Page(BaseHTTPRequestHandler):
    """Answer every request with the page above."""

    def do_GET(self) -> None:
        """Send the page."""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PAGE.encode())

    def log_message(self, *args: object) -> None:
        """Print nothing for a request."""


server = HTTPServer(("127.0.0.1", 0), Page)
threading.Thread(target=server.serve_forever, daemon=True).start()
address = f"http://127.0.0.1:{server.server_port}/"

fetch_url = tool("fetch_url", ["url"])
text = fetch_url(url=address)

check(not is_error(text), "A page that exists comes back as text.", text)
check("Lighthouse" in text and "twice" in text, "The words of the page are kept.", text)
check("<" not in text and ">" not in text, "Tags are removed.", text)
check("crimson" not in text, "The contents of a style element are removed.", text)
check("secretvalue" not in text, "The contents of a script element are removed.", text)
check(len(text) <= 8000, "The text is cut at 8,000 characters.", len(text))

server.shutdown()
server.server_close()  # so the next request is refused at once
refused = fetch_url(url=address)
check(is_error(refused), "A page that cannot be reached returns Error: ...", refused)
print("ok")
