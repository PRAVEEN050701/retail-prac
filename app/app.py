from http.server import BaseHTTPRequestHandler, HTTPServer

VERSION = "1.0.1"


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                f"Retail App - Version {VERSION}".encode()
            )


server = HTTPServer(("0.0.0.0", 8081), Handler)

print(f"Retail App - Version {VERSION}")
print("Running on port 8081")

server.serve_forever()