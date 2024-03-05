import argparse
import asyncio

from py_terminal_chat import __version__
from py_terminal_chat.server.handler import ClientHandler


def cli_args():
    parser = argparse.ArgumentParser(
        description="py-terminal-chat(server):A simple chat server written in Python using asyncio and tcp sockets."
    )

    # Add version argument
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s v{__version__}"
    )

    # Add room name argument
    parser.add_argument(
        "--name",
        type=str,
        default="Python Terminal Chat-Room",
        help="Name for the chat room",
    )

    # Add ports argument
    parser.add_argument(
        "--port", "-p", type=int, default=8081, help="Port to run the server on"
    )

    # Number of recent messages to store
    parser.add_argument(
        "--nhistory",
        "-n",
        type=int,
        default=10,
        help="Number of recent messages to store",
    )

    args = parser.parse_args()
    return args


def main():
    async def run_server():
        try:
            args = cli_args()
            handler = ClientHandler(args.name, args.nhistory)
            srv = await asyncio.start_server(
                handler.accept_connections, "0.0.0.0", args.port
            )
            await srv.serve_forever()

        except Exception as e:
            print(f"Exception occurred, details: {repr(e)}")

        finally:
            srv.close()
            await srv.wait_closed()

    asyncio.run(run_server(), debug=False)
