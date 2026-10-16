"""
overX - Web UI Server (Dropship.io Monochrome Edition)
Full Product Intelligence with Live Images, Ratings, Reviews & Affiliate Commission
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from shopee_parser import ShopeeProductParser

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class OverXHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html_path = os.path.join(BASE_DIR, "index.html")
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "index.html not found")
            return

        elif self.path == "/logo.png":
            logo_path = os.path.join(BASE_DIR, "logo.png")
            if os.path.exists(logo_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(logo_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "logo.png not found")
            return

        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        if self.path == "/api/check":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                payload = json.loads(body)
                url = payload.get("url", "").strip()
            except Exception:
                url = ""

            # ดึงข้อมูลสินค้าแบบครบวงจร
            result_data = ShopeeProductParser.parse_full_product(url)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result_data, ensure_ascii=False).encode("utf-8"))
            return

        self.send_error(404, "API endpoint not found")

def start_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, OverXHandler)
    url = f"http://localhost:{PORT}"
    
    print("\n" + "="*65)
    print("⚡ OVERX — Dropship.io Monochrome Edition")
    print("="*65)
    print(f"🌐 Server running at: {url}")
    print(f"👉 Real-time Image Gallery, Ratings, Reviews & Commission active")
    print("="*65 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopped OVERX server.")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
