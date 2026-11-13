# -*- coding: utf-8 -*-
"""Local loopback HTTP server with atomic progress backup for the Learning Roadmap."""
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "roadmap-state.json"
MAX_BODY_BYTES = 20 * 1024 * 1024


class RoadmapHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        # Keep console output quiet and clean unless error.
        if args and len(args) >= 2 and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)

    def _send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _same_origin(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        parsed = urlparse(origin)
        host = self.headers.get("Host", "")
        return parsed.scheme == "http" and parsed.netloc == host

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json(HTTPStatus.OK, {"ok": True, "root": str(ROOT)})
            return
        if path == "/api/state":
            if not STATE_FILE.exists():
                self._send_json(HTTPStatus.NOT_FOUND, {"exists": False})
                return
            try:
                raw = STATE_FILE.read_text(encoding="utf-8")
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise ValueError("invalid state")
            except Exception:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False})
                return
            self._send_json(HTTPStatus.OK, {"exists": True, "state": data})
            return
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/state":
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False})
            return
        if not self._same_origin():
            self._send_json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "origin"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False})
            return
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False})
            return
        if not isinstance(data, dict) or data.get("v") != 3:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False})
            return
        tmp = STATE_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, STATE_FILE)
        self._send_json(HTTPStatus.OK, {"ok": True})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path != "/api/state":
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False})
            return
        if not self._same_origin():
            self._send_json(HTTPStatus.FORBIDDEN, {"ok": False})
            return
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        self._send_json(HTTPStatus.OK, {"ok": True})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), RoadmapHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

