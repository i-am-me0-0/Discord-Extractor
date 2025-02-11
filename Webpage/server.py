import os
import json
import requests
from urllib.parse import urlparse, parse_qs
from http.server import SimpleHTTPRequestHandler, HTTPServer


class CustomHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Required for SharedArrayBuffer (enables Cross-Origin Isolation) for ffmpeg.wasm
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()
    def do_GET(self):
        if self.path.startswith("/download-sticker"):
            self.download_sticker()
        elif self.path == "/sticker.json":
            self.serve_sticker_json()
        else:
            super().do_GET()

    def download_sticker(self):
        # Extract sticker ID from URL query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)
        sticker_id = params.get("id", [""])[0]

        if not sticker_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No sticker ID provided."}).encode())
            return

        sticker_url = f"https://cdn.discordapp.com/stickers/{sticker_id}.json"
                # Ensure sticker_cache folder exists
        cache_dir = "sticker_cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # json_file_path = os.path.join(cache_dir, f"sticker_{sticker_id}.json")
        json_file_path = os.path.join(cache_dir, f"sticker.json")
        try:
            response = requests.get(sticker_url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            # Save the sticker JSON inside the sticker_cache folder
            with open(json_file_path, "wb") as f:
                f.write(response.content)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Sticker downloaded successfully!", "file": json_file_path}).encode())

        except requests.exceptions.RequestException as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_sticker_json(self):
            json_file_path = os.path.join("sticker_cache", "sticker.json")

            if os.path.exists(json_file_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                with open(json_file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Sticker file not found."}).encode())

if __name__ == "__main__":
    PORT = 9000
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, CustomHandler)


    print(f"Serving on http://localhost:{PORT}")
    httpd.serve_forever()
