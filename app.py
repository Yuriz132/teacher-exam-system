import http.server
import urllib.request
import json
import os

# Cloud platform: use environment variable PORT, default to 8765
PORT = int(os.environ.get("PORT", 8765))
HTML_FILE = "???????? (2).html"
XUNFEI_BASE = os.environ.get("XUNFEI_BASE", "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2")

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/" + HTML_FILE
        return super().do_GET()

    def do_POST(self):
        if self.path == "/chat/completions":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            req = urllib.request.Request(
                f"{XUNFEI_BASE}/chat/completions",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.headers.get("Authorization", ""),
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": str(e)}).encode()
                )
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"?????????? http://localhost:{PORT}")

http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler).serve_forever()
