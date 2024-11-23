import http.server 
import os
import re
import socket

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Check if the request is for the GIF file
        if self.path == "/artifact.gif":
            file_path = "artifact.gif"
            
            # Check if the file exists
            if os.path.exists(file_path):
                try:
                    # Open and send the GIF file
                    with open(file_path, "rb") as f:
                        # Send the response header
                        self.send_response(200)
                        self.send_header("Content-type", "image/gif")
                        self.end_headers()
                        
                        # Send the image data
                        self.wfile.write(f.read())
                    return
                except Exception as e:
                    # Error reading file
                    self.send_response(500)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"<html><body>Error reading image: {e}</body></html>".encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body>Image not found</body></html>")

        # If the request is for the main page, show the upload form
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>HTTP Image Uploader</title>
                <style>
                    body {
                        background-color: #c3c3c3;
                        font-family: Geneva, sans-serif;
                        margin: 0;
                        padding-bottom: 50px; /* Make space for the footer */
                        min-height: 100vh; /* Ensures the body takes up at least the full height of the viewport */
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

            # Split the body by the boundary
            parts = body.split(b"--" + boundary)
            for part in parts:
                if b"Content-Disposition" in part:
                    match = re.search(b'filename="([^"]+)"', part)
                    if match:
                        filename = match.group(1).decode()
                        header, file_data = part.split(b"\r\n\r\n", 1)
                        file_data = file_data.rsplit(b"\r\n", 1)[0]

                        # Save the file
                        with open(filename, "wb") as f:
                            f.write(file_data)

                        # Send a success message
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>HTTP Image Uploader</title>
                            <style>
                                body {{
                                    background-color: #c3c3c3;
                                    font-family: Geneva, sans-serif;
                                    margin: 0;
                                    text-align: center;
                                    min-height: 100vh; /* Ensures the body takes up at least the full height of the viewport */
                                }}
                                .dialog {{
                                    background-color: #d0f0c0;
                                    border: 2px solid black;
                                    padding: 20px;
                                    width: 300px;
                                    text-align: center;
                                    margin: 20px auto;
                                }}
                                .dialog h1 {{
                                    font-size: 18px;
                                    margin-bottom: 20px;
                                    color: black;
                                }}
                                .dialog a {{
                                    text-decoration: none;
                                    color: blue;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="dialog">
                                <h1>Upload Successful</h1>
                                <p>File '{filename}' uploaded successfully!</p>
                                <a href="/">Back to Upload</a>
                            </div>
                            <footer>
                                <p>Created by Xenocide21 | Date: 22-11-24</p>
                            </footer>
                        </body>
                        </html>
                        """.encode())
                        return

            # If no file found
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No file found in the upload.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid form submission.")

def get_local_ip():
    """Get the local machine's IP address for all network interfaces"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Connect to a remote server and retrieve the local address used for the connection
        s.connect(('10.254.254.254', 1))  # Arbitrary remote address
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'  # Fallback to localhost if connection fails
    finally:
        s.close()
    return local_ip

if __name__ == "__main__":
    PORT = 8080
    local_ip = get_local_ip()  # Get the local IP address
    server = http.server.HTTPServer((local_ip, PORT), SimpleHTTPRequestHandler)
    print(f"Serving on http://{local_ip}:{PORT}")
    server.serve_forever()
