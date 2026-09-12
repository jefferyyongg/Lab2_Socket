"""
Lab 2 - Multiple Sockets / Chat Room (Server)
NAME:
STUDENT ID:
DESCRIPTION:
"""


def serve(port):
    """
    Run the plain-TCP chat server on the supplied port.

    port: The TCP port on which the server listens.
    """
    pass


# Command-line parser. Do not change this part.
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port to listen on", default=12345, type=int)
    arguments = parser.parse_args(sys.argv[1:])
    serve(arguments.port)
