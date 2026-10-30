#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import base64
from datetime import datetime
from pathlib import Path
import threading


KEY = b"secretkey"
OUTPUT_DIR = Path(__file__).resolve().parent
file_lock = threading.Lock()


class EchoHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.echo()

    def do_POST(self):
        self.echo()

    def do_PUT(self):
        self.echo()

    def do_PATCH(self):
        self.echo()

    def do_DELETE(self):
        self.echo()

    def do_OPTIONS(self):
        self.echo()

    def do_HEAD(self):
        self.echo()

    def echo(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        try:
            # Step 1: Base64 decode
            decoded = base64.b64decode(body, validate=True)

            # Step 2: XOR with repeating key
            result = bytes(
                byte ^ KEY[i % len(KEY)]
                for i, byte in enumerate(decoded)
            )

            # Step 3: Determine file type
            type_id = self.headers.get("type-ID", "").strip()

            if type_id == "0":
                # Append text to text.txt
                filepath = OUTPUT_DIR / "text.txt"

                with file_lock:
                    with filepath.open("ab") as f:
                        f.write(result)
                        #f.write(b"\n")

                print(f"[+] Appended {len(result)} bytes to text.txt")

            else:
                # Save binary files separately
                extension = ".png" if type_id == "1" else ".bin"

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{timestamp}{extension}"
                filepath = OUTPUT_DIR / filename

                with file_lock:
                    filepath.write_bytes(result)

                print(f"[+] Saved {filename} ({len(result)} bytes)")

            # Step 4: Echo transformed body back to client
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/octet-stream"
            )
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(result)

        except Exception as e:
            error = f"Error processing request: {e}".encode()

            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(error)))
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(error)


# Start HTTP server
server = ThreadingHTTPServer(("0.0.0.0", 8080), EchoHandler)

print("HTTP Echo Server running at http://localhost:8080")
print(f"Saving received files to: {OUTPUT_DIR}")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server...")
    server.shutdown()
    server.server_close()

