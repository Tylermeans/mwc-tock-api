#!/usr/bin/env python3
"""Zero-dependency local dev server for the Midwest Cards reservation board.

Serves the board at / and a live mock /waitlist.json so you can iterate on the UI
without n8n or Tock. The mock times are generated around "now" so the board looks
live. Run from anywhere:

    python3 dev/dev-server.py

Then open:  http://localhost:8000/?data=/waitlist.json
"""
import datetime
import http.server
import json
import os
import socketserver
import urllib.parse

PORT = int(os.environ.get("PORT", "8000"))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root


def _fmt(t):
    # 12-hour, no leading zero, cross-platform
    try:
        return t.strftime("%-I:%M %p")
    except ValueError:
        return t.strftime("%#I:%M %p")


def mock_feed():
    now = datetime.datetime.now().replace(second=0, microsecond=0)

    def slot(mins):
        return _fmt(now + datetime.timedelta(minutes=mins))

    people = [
        (-20, "Marcus", "T", "seated"),
        (-5,  "Priya",  "N", "seated"),
        (10,  "Devon",  "R", "upcoming"),
        (25,  "Sofia",  "L", "upcoming"),
        (40,  "Elijah", "B", "upcoming"),
        (55,  "Hannah", "K", "upcoming"),
        (70,  "Andre",  "W", "upcoming"),
    ]
    return {
        "updatedAt": datetime.datetime.now().astimezone().isoformat(),
        "reservations": [
            {"time": slot(m), "firstName": f, "lastInitial": li, "status": s}
            for (m, f, li, s) in people
        ],
    }


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/waitlist.json":
            body = json.dumps(mock_feed()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/":
            self.path = "/board/index.html"
        return super().do_GET()

    def log_message(self, fmt, *args):
        pass  # quiet


if __name__ == "__main__":
    os.chdir(ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Midwest Cards board dev server")
        print(f"  Board:  http://localhost:{PORT}/?data=/waitlist.json")
        print(f"  Feed:   http://localhost:{PORT}/waitlist.json")
        print("  Ctrl-C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
