"""
Lab 2 - Multiple Sockets / Chat Room (Server)
NAME:
STUDENT ID:
DESCRIPTION:
"""
import select
import socket
import sys

def serve(port):
    """
    Run the plain-TCP chat server on the supplied port.

    port: The TCP port on which the server listens.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_ip = "127.0.0.1"
    s.bind((server_ip, port))
    s.listen(1)

    inputs = [s]
    clients = {}

    while True:
            readable, _, exceptional = select.select(inputs, [], inputs)

            for current_socket in readable:
                # if listening socket is active meaning client is trying to connect
                if current_socket is s:
                    client_socket, client_address = current_socket.accept()
                    # s.accept and add them to socket list
                    inputs.append(client_socket)
                    clients[client_socket] = {"address": client_address, "nickname": "", "buffer": ""}
                    print(clients)
                # else any other activity(messages, disconnect, err)
                else:
                    # parse messages
                    data = current_socket.recv(1024)

                    # if anything other than messages -> disconnect
                    if not data:
                        inputs.remove(current_socket)
                        del clients[current_socket]
                        current_socket.close()
                    # else parse messages to buffer
                    else:
                        clients[current_socket]["buffer"] += data.decode("utf-8")

# Command-line parser. Do not change this part.
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port to listen on", default=12345, type=int)
    arguments = parser.parse_args(sys.argv[1:])
    serve(arguments.port)
