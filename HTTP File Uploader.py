import http.server
import os
import re
import socket

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the artifact.gif file
        if self.path == "/artifact.gif":
            file_path = "artifact.gif"
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-type", "image/gif")
                        self.end_headers()
                        self.wfile.write(f.read())
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"<html><body>Error reading image: {e}</body></html>".encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body>Image not found</body></html>")

        # List files in the root directory
        elif self.path == "/list":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            files = [
                f for f in os.listdir(".")
                if os.path.isfile(f) and not f.endswith(".py") and f != "artifact.gif"
            ]
            file_links = "".join(
                f'<li><a href="/{file}">{file}</a></li>' for file in files
            )
            self.wfile.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>File Index</title>
                <style>
                    body {{
                        background-color: #c3c3c3;
                        font-family: Geneva, sans-serif;
                        margin: 0;
                        padding-bottom: 50px;
                        min-height: 100vh;
                    }}
                    .dialog {{
                        background-color: #e0e0e0;
                        border: 2px solid black;
                        padding: 20px;
                        width: 400px;
                        text-align: center;
                        margin: 20px auto;
                    }}
                    .dialog ul {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    .dialog ul li {{
                        margin: 10px 0;
                    }}
                    .dialog a {{
                        text-decoration: none;
                        color: blue;
                    }}
                    .dialog a:hover {{
                        text-decoration: underline;
                    }}
                    .dialog h1 {{
                        font-size: 18px;
                        margin-bottom: 20px;
                        color: black;
                    }}
                    footer {{
                        text-align: center;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="dialog">
                    <h1>File Index</h1>
                    <ul>
                        {file_links}
                    </ul>
                    <a href="/">Back to Upload Page</a>
                </div>
                <footer>
                    <p>Created by Xenocide21 | Date: 22-11-24</p>
                </footer>
            </body>
            </html>
            """.encode())

        # Main page with upload form and gif
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>HTTP File Uploader</title>
                <style>
                    body {
                        background-color: #c3c3c3;
                        font-family: Geneva, sans-serif;
                        margin: 0;
                        padding-bottom: 50px; 
                        min-height: 100vh; 
                    }
                    .dialog {
                        background-color: #e0e0e0;
                        border: 2px solid black;
                        padding: 20px;
                        width: 300px;
                        text-align: center;
                        margin: 20px auto;
                    }
                    .dialog h1 {
                        font-size: 18px;
                        margin-bottom: 20px;
                        color: black;
                    }
                    .dialog form {
                        margin: 0;
                    }
                    .dialog input[type="file"] {
                        margin: 10px 0;
                    }
                    .dialog input[type="submit"] {
                        padding: 5px 10px;
                        background-color: #c3c3c3;
                        border: 2px solid black;
                        cursor: pointer;
                    }
                    .dialog input[type="submit"]:hover {
                        background-color: #d3d3d3;
                    }
                    .gif-container {
                        text-align: center;
                        margin-bottom: 20px;
                    }
                    footer {
                        text-align: center;
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="dialog">
                    <div class="gif-container">
                        <img src="/artifact.gif" alt="Artifact GIF" width="250">
                    </div>
                    <h1>Upload File</h1>
                    <form enctype="multipart/form-data" method="post">
                        <input name="file" type="file" />
                        <input type="submit" value="Upload" />
                    </form>
                    <div>
                        <a href="/list">View File Index</a>
                    </div>
                </div>
                <footer>
                    <p>Created by Xenocide21 | Date: 22-11-24</p>
                </footer>
            </body>
            </html>
            """)

    def do_POST(self):
        # Handle file uploads
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        if "multipart/form-data" in content_type:
            boundary = content_type.split("boundary=")[1].encode()
            body = self.rfile.read(content_length)
            parts = body.split(b"--" + boundary)
            for part in parts:
                if b"Content-Disposition" in part:
                    match = re.search(b'filename="([^"]+)"', part)
                    if match:
                        filename = match.group(1).decode()
                        header, file_data = part.split(b"\r\n\r\n", 1)
                        file_data = file_data.rsplit(b"\r\n", 1)[0]
                        with open(filename, "wb") as f:
                            f.write(file_data)
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(f"File '{filename}' uploaded successfully!".encode())
                        return
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No file found in the upload.")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

if __name__ == "__main__":
    PORT = 8080
    local_ip = get_local_ip()
    server = http.server.HTTPServer((local_ip, PORT), SimpleHTTPRequestHandler)
    print(f"Serving on http://{local_ip}:{PORT}")
    server.serve_forever()
