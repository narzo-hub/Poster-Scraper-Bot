from http.server import BaseHTTPRequestHandler, HTTPServer
PORT = 8000  

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"@EchoBotz"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"WAB server bonded at {PORT}")
    server.serve_forever()
