"""
Lab 2 - Single Socket / HTTP Server
NAME: Jeffery Yong
STUDENT ID: 16385179
DESCRIPTION: /
"""

import mimetypes
import os
import socket
from datetime import datetime, timezone

def keepCurrentCookieCount(current_cookies):
    lines = current_cookies.split("\n", -1)
    for l in lines:
        if "nns26-visit-count" in l:
            count = int(l.split("=")[1])
            return f"nns26-visit-count={count}; Max-Age=2592000; Path=/; SameSite=Lax"

def updateCookies(current_cookies):
    lines = current_cookies.split("\n", -1)
    for l in lines:
        if "nns26-visit-count" in l:
            count = int(l.split("=")[1])
            if count >= 1:
                count += 1
                print(f"curr numba: {count}")
                return f"nns26-visit-count={count}; Max-Age=2592000; Path=/; SameSite=Lax"
            else:
                return "nns26-visit-count=1; Max-Age=2592000; Path=/; SameSite=Lax"

def cookiesExists(current_cookies):
    lines = current_cookies.split("\n", -1)
    exists = False
    for l in lines:
        if "nns" in l:
            exists = True

    return exists

def http_date():
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

def build_response(status, body=b"", content_type="text/html", set_cookies="nns26-visit-count=1; Max-Age=2592000; Path=/; SameSite=Lax"):
    header = (
        f"HTTP/1.1 {status}\r\n" +
         "Connection: close\r\n" +
        f"Content-type: {content_type}\r\n" +
         f"Content-Length: {len(body)}\r\n" +
         f"Set-Cookie: {set_cookies}\r\n" +
         f"Date: {http_date()}\r\n" +
          "Server: Jeff\r\n\r\n"
    )
    return header.encode("utf-8") + body

# This is just an example of how you could implement the server. You may change
# this however you wish.
# For example, you could do a really nice object oriented version if you like.

def serve(port, public_html):
    """
    The entry point of the HTTP server.
    port: The port to listen on.
    public_html: The directory where all static files are stored.
    """
    # setup socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """
    Important: make sure to set the reusable address option, SO_REUSEADDR (see the Python
    documentation on the socket module), reason = docs: the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire.
    """
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind socket to listening ip/port
    server_ip = "127.0.0.1"
    s.bind((server_ip, port))

    # listen to incoming connections, when 0 only one client connection can be established at a time
    # when having listen(1) socket lets many clients wait in queue until accept is called on a client
    # once accept is called, the client leaves the queue and the slot free's up for the next client
    s.listen(0)

    while True:
        # stalls execution thread until client connects -> then returns a pair of (conn, addr) tuple
        # address is tuple of clients IP: [0] and port: [1]
        # socket is a new socket object which shares connection with the client and can be used to communicate
        client_socket, client_address = s.accept()
        print(f"Accepted connection from: {client_address[0]} to: {client_address[1]}")

        # empty bytes litteral
        buffer = b""
        while True:
            request = client_socket.recv(1024) #buffer length

            # if received request isn't eof then add to buffer
            if "\r\n\r\n" not in request.decode("utf-8"):
                buffer += request
            else:
                buffer += request
                break

        buffer = buffer.decode("utf-8") # decode entire message/header as bytes into string

        # split header part of buffer(method, path, version)
        split_buffer = buffer.split("\r\n", 1)

        # end of split gets appended as one string -> our body
        client_request = split_buffer[0].split(" ", 2)
        client_body = split_buffer[1]

        request_method = client_request[0]
        request_path = client_request[1]
        request_version = client_request[2]

        # close when client exits
        if request_method.lower() != "get":
            # close socket on server side and break out of the infinite loop
            response = build_response("501 Not Implemented", b"501 Not Implemented", "text/plain")
            client_socket.sendall(response)
            client_socket.close()
        else:
            increment_cookies = False
            if request_path == "/" or "/index.html" in request_path:
                request_path = "/index.html"
                increment_cookies = True

            # format and join path with ./public_html
            safe_path = os.path.normpath(request_path).lstrip("/\\")
            file_path = os.path.join(public_html, safe_path)

            try:
                with open(file_path, "rb") as f:
                    body = f.read()

                content_type = mimetypes.guess_type(file_path)[0]
                print(cookiesExists(client_body))
                if cookiesExists(client_body):
                    if increment_cookies:
                        response = build_response("200 OK", body, content_type, updateCookies(client_body))
                    else:
                        response = build_response("200 OK", body, content_type, keepCurrentCookieCount(client_body))
                else:
                    response = build_response("200 OK", body, content_type)

            except FileNotFoundError:
                response = build_response("404 Not Found", b"404 Not Found", "text/plain")

            client_socket.sendall(response)
            client_socket.close()

# This the entry point of the script.
# Do not change this part.
if __name__ == "__main__":
    import os
    import sys
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--port", help="port to bind to", default=8086, type=int)
    p.add_argument("--public_html", help="home directory", default="./public_html")
    args = p.parse_args(sys.argv[1:])
    public_html = os.path.abspath(args.public_html)
    serve(args.port, public_html)
