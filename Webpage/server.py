import os
import json
import requests
from urllib.parse import urlparse, parse_qs
from http.server import SimpleHTTPRequestHandler, HTTPServer
import hashlib


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
        elif self.path.startswith("/save-image"):
            self.save_image()
        elif self.path.startswith("/list-images"):  # New route
            self.list_images()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == "/upload":
            self.handle_file_upload()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_file_upload(self):
        content_length = int(self.headers["Content-Length"])
        content_type = self.headers["Content-Type"]

        if "multipart/form-data" not in content_type:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid content type"}).encode())
            return

        boundary = content_type.split("boundary=")[-1].encode()
        body = self.rfile.read(content_length)

        # Parse file data from multipart form
        parts = body.split(boundary)
        file_data = None
        file_name = "uploaded_file.gif"

        for part in parts:
            if b"Content-Disposition: form-data;" in part:
                headers, file_content = part.split(b"\r\n\r\n", 1)
                if b"filename=" in headers:
                    file_name = headers.split(b'filename="')[1].split(b'"')[0].decode()
                file_data = file_content.rstrip(b"--\r\n")

        if not file_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No file data received"}).encode())
            return

        # Save file to server
        save_dir = "saved_images"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)

        with open(file_path, "wb") as f:
            f.write(file_data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "File uploaded successfully!", "file": file_path}).encode())


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
                with open(json_file_path, "rb") as f:
                    content = f.read()
        
                etag = hashlib.md5(content).hexdigest()  # Generate an ETag from the file's hash

                # Check if the client already has the latest version
                if "If-None-Match" in self.headers and self.headers["If-None-Match"] == etag:
                    self.send_response(304)  # Not Modified
                    self.end_headers()
                    return

                self.send_response(200)
                # Add headers to prevent caching
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")  # For HTTP/1.0 compatibility
                self.send_header("Expires", "0")  # Ensures that the content is not cached

                self.send_header("Content-Type", "application/json")
                self.end_headers()
                with open(json_file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Sticker file not found."}).encode())


    def save_image(self):
        url = self.get_query_param("url")
        file_name = self.get_query_param("name")
        if not url or not file_name:
            self.respond(400, {"error": "Missing image URL or name."})
            return

        save_dir = "saved_images"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)

        self.download_file(url, file_path)

    def download_file(self, url, file_path):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(response.content)

            self.respond(200, {"success": True,"message": "File saved successfully!", "file": file_path})
        except requests.exceptions.RequestException as e:
            self.respond(500, {"error": str(e)})

    def get_query_param(self, key):
        return parse_qs(urlparse(self.path).query).get(key, [""])[0]

    def respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def list_images(self):
        image_dir = "saved_images"
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        categorized_images = {"root": [], "folders": {}}

        # Walk through the directory
        for root, dirs, files in os.walk(image_dir):
            relative_path = os.path.relpath(root, image_dir)
            
            # Ignore root "." and set images in the main directory
            if relative_path == ".":
                categorized_images["root"] = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            else:
                categorized_images["folders"][relative_path] = [
                    f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                ]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(categorized_images).encode())

if __name__ == "__main__":
    PORT = 9000
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, CustomHandler)


    print(f"Serving on http://localhost:{PORT}")
    httpd.serve_forever()
