import argparse
import asyncio
import curses

import _curses

from py_terminal_chat import __version__
from py_terminal_chat.client.client import ChatClient
from py_terminal_chat.client.gui import ChatWindow, InputWindow


def cli_args():
    parser = argparse.ArgumentParser(
        description="py-terminal-chat(client):A simple chat client with a terminal gui, written in Python using "
        "asyncio and curses"
    )

    # Add version argument
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s v{__version__}"
    )

    # Add ports argument
    parser.add_argument(
        "--port", "-p", type=int, default=8081, help="server port to connect to"
    )

    # Add host address argument
    parser.add_argument(
        "--server",
        "-s",
        type=str,
        default="localhost",
        help="server address to connect to",
    )

    args = parser.parse_args()
    return args


def main():
    async def runner(stdscr: "_curses.window", host: str, port: int):
        chat_client = ChatClient(host, port)
        if not await chat_client.prompt():
            return

        my, mx = stdscr.getmaxyx()
        chat_window = ChatWindow(mx, my)
        input_window = InputWindow(mx, my)

        curses.cbreak()
        stdscr.keypad(True)
        stdscr.clear()

        await chat_client.load_history(chat_window)
        await chat_client.run(input_window, chat_window)

        curses.nocbreak()
        stdscr.keypad(False)
        curses.endwin()

    args = cli_args()
    asyncio.run(curses.wrapper(runner, args.server, args.port))
