"""
Lab 2B - Multiple Sockets / Chat Room (Client)
DESCRIPTION: This file contains the implementation of a chat client. The client
is kept as dumb as possible; the server has to do all the work. The client will
connect to 127.0.0.1:12345 unless told otherwise using --port and --ip.

DO NOT MODIFY THIS FILE!
"""

import select
import socket
import sys
from threading import Thread

from gui import MainWindow


class ChatClient(Thread):
    def __init__(self, port, ip, window):
        """
        port: TCP port to connect to.
        ip: IP address to connect to.
        window: GUI window used for input and output.
        """
        super().__init__()

        self.window = window
        self.wake_socket = self.window.wake_thread

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        self.socket = client_socket

    def run(self):
        """Receive messages until the server or GUI closes the connection."""
        while not self.window.quit_event.is_set():
            inputs = [self.socket, self.wake_socket]
            readable, _, exceptional = select.select(inputs, [], [self.socket])

            if self.socket in exceptional:
                self.window.writeln("The server connection failed. Close the program.")
                self.window.stop()
                return

            for readable_object in readable:
                if readable_object is self.socket:
                    data = self.socket.recv(4096)
                    if not data:
                        self.window.writeln("The server is down. Close the program.")
                        self.window.stop()
                        return
                    self.window.write(data.decode("utf-8", errors="replace"))

                elif readable_object is self.wake_socket:
                    self.socket.close()
                    return

    def text_entered(self, line):
        """Send one newline-terminated protocol command to the server."""
        self.socket.sendall((line + "\n").encode("utf-8"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port to connect to", default=12345, type=int)
    parser.add_argument("--ip", help="IP address to connect to", default="127.0.0.1")
    arguments = parser.parse_args(sys.argv[1:])

    main_window = MainWindow()
    client = ChatClient(arguments.port, arguments.ip, main_window)
    main_window.set_client(client)
    client.start()
    main_window.start()
