from urllib.parse import unquote
import http.server
import os
import re
import socket

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        image_map = {
            "/artifact.gif": "artifact.gif",
            "/server.gif": "server.gif",
            "/webicon.gif": "webicon.gif"
        }

        # Check if the path matches one of the image files
        if self.path in image_map:
            file_path = image_map[self.path]
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
            
            # List files from the root directory (excluding certain files) and from the 'downloads' folder
            files = []
            directories_to_check = ["./downloads"]
            for directory in directories_to_check:
                if os.path.exists(directory):
                    files.extend([
                        f for f in os.listdir(directory)
                        if os.path.isfile(os.path.join(directory, f)) and not f.endswith(".py") and f != "artifact.gif" and f != "server.gif" and f != "webicon.gif"
                    ])
             # Generate the links for the files found
            file_links = "".join(
                f'<li><a href="/download/{file}">{file}</a></li>' for file in files
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

        # Handle file downloads
        elif self.path.startswith("/download/"):
            file_name = self.path[len("/download/"):]
            
            # Decode URL-encoded string (e.g., '%20' becomes a space)
            file_name = unquote(file_name)

            # Check in the root directory and the 'downloads' folder
            directories_to_check = ["./downloads"]
            for directory in directories_to_check:
                file_path = os.path.join(directory, file_name)
                if os.path.isfile(file_path):
                    # Serve the file if found
                    self.send_response(200)
                    self.send_header("Content-type", "application/octet-stream")
                    self.send_header("Content-Disposition", f"attachment; filename={file_name}")
                    self.end_headers()
                    with open(file_path, "rb") as file:
                        self.wfile.write(file.read())
                    return
                    self.send_response(500)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"<html><body>Error downloading file: {e}</body></html>".encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body>File not found</body></html>")

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
                    table {
                        width: 100%;
                        margin-top: 20px;
                        margin-bottom: 20px;
                    }
                    .panel {
                        background-color: #e0e0e0;
                        border: 2px solid black;
                        padding: 20px;
                        width: 240px;
                        height: 350px;
                        text-align: center;
                        position: relative; /* Allow absolute positioning of the icon */
                    }
                    .sidebar {
                        width: 300px;
                    }
                    .sidebar h2 {
                        font-size: 16px;
                        color: black;
                        margin-bottom: 10px;
                    }
                    .sidebar ul {
                        list-style-type: none;
                        padding: 0;
                        margin: 0;
                    }
                    .sidebar ul li {
                        margin: 5px 0;
                        background-color: #c3c3c3;
                        border: 2px solid black;
                    }
                    .sidebar ul li:hover {
                        background-color: #d3d3d3;
                    }
                    .sidebar ul li a {
                        text-decoration: none;
                        color: #0066cc;  /* Link color */
                        display: block;  /* Ensure the whole area is clickable */
                        padding: 5px 10px; /* Add some padding for the hover effect */
                    }
                    .sidebar ul li a:hover {
                        text-decoration: underline;
                        color: #0044aa; /* Hover color */
                        background-color: #d3d3d3; /* Darker grey background on hover */
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
                    .gif-container img {
                        width: 140px; /* Resize the GIF */
                        height: auto; /* Maintain aspect ratio */
                    }
                    footer {
                        clear: both;
                        text-align: center;
                        margin-top: 20px;
                    }
                    /* Styling for the icons */
                    .icon {
                        position: absolute;
                        top: 8px;
                        right: 10px;
                        width: 50px;  /* Set to 25px as requested */
                        height: auto;
                    }
                </style>
            </head>
            <body>
                <table>
                    <tr>
                        <!-- Sidebar -->
                        <td class="sidebar" valign="top">
                            <div class="panel">
                                <!-- Useful Links box icon -->
                                <img src="/webicon.gif" class="icon" alt="Useful Links Icon">
                                <h2>Useful Links</h2>
                                <ul>
                                    <li><a href="http://macintoshgarden.org" target="_blank">Macintosh Garden</a></li>
                                    <li><a href="http://macintoshrepository.org" target="_blank">Macintosh Repository</a></li>
                                    <li><a href="http://archive.org" target="_blank">Archive.org</a></li>
                                    <li><a href="http://frogfind.com" target="_blank">Frogfind</a></li>
                                    <li><a href="http://theoldnet.com" target="_blank">The Old Net</a></li>
                                    <li><a href="http://retronetwork.net" target="_blank">RetroNetwork</a></li>
                                </ul>
                            </div>
                        </td>
                        <!-- Main file upload section -->
                        <td class="dialog" valign="top">
                            <div class="panel">
                                <!-- HTTP File Server box icon -->
                                <img src="/server.gif" class="icon" alt="HTTP File Server Icon">
                                <h1> HTTP File Server </h1>
                                <div class="gif-container">
                                    <img src="/artifact.gif" alt="Artifact GIF">
                                </div>
                                <h1>Upload File</h1>
                                <form enctype="multipart/form-data" method="post">
                                    <input name="file" type="file" />
                                    <input type="submit" value="Upload File" />
                                </form>
                                <div>
                                    <a href="/list">View All Files</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
                <footer>
                    <p>Created by Xenocide21 | Date: 22-11-24</p>
                    <p>Arbitration: <a href="https://www.vecteezy.com/free-vector/internet-icon">Internet Icon Vectors by Vecteezy</a> <a href="https://www.vecteezy.com/free-vector/network-server">Network Server Vectors by Vecteezy</a> </p>
                </footer>
            </body>
            </html>
            """)

    def do_POST(self):
        # Handle file uploads
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        
        # Ensure the multipart form-data is detected
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
                        
                        # Save file to /downloads folder
                        download_dir = './downloads'
                        if not os.path.exists(download_dir):
                            os.makedirs(download_dir)  # Create directory if it doesn't exist
                        
                        file_path = os.path.join(download_dir, filename)
                        with open(file_path, "wb") as f:
                            f.write(file_data)
                        
                        # Display success page with consistent style
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>Upload Success</title>
                            <style>
                                body {{
                                    background-color: #c3c3c3;
                                    font-family: Geneva, sans-serif;
                                    margin: 0;
                                    padding-bottom: 50px;
                                    min-height: 100vh;
                                }}
                                .dialog {{
                                    background-color: #e0f7e0;
                                    border: 2px solid black;
                                    padding: 20px;
                                    width: 300px;
                                    text-align: center;
                                    margin: 20px auto;
                                }}
                                .dialog h1 {{
                                    font-size: 18px;
                                    margin-bottom: 20px;
                                    color: green;
                                }}
                                .dialog p {{
                                    color: black;
                                    font-size: 16px;
                                }}
                                .dialog a {{
                                    text-decoration: none;
                                    color: blue;
                                }}
                                .dialog a:hover {{
                                    text-decoration: underline;
                                }}
                                footer {{
                                    text-align: center;
                                    margin-top: 20px;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="dialog">
                                <h1>File Uploaded Successfully!</h1>
                                <p>File: <strong>{filename}</strong></p>
                                <a href="/">Back to Upload Page</a>
                            </div>
                            <footer>
                                <p>Created by Xenocide21 | Date: 22-11-24</p>
                            </footer>
                        </body>
                        </html>
                        """.encode())
                        return
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body>Error processing request</body></html>")
        
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
