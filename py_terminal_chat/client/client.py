import asyncio
import concurrent.futures
from typing import Protocol

from py_terminal_chat.utils import read_from_stream, write_to_stream


class InputWindow(Protocol):
    def refresh(self) -> None: ...

    def get_input_message(self) -> str: ...


class ChatWindow(Protocol):
    def add_message(self, message: str): ...


class ChatClient:
    def __init__(self, addr: str, port: int) -> None:
        self.addr = addr
        self.port = port
        self.stop_signal = asyncio.Event()

    async def prompt(self):
        self.reader, self.writer = await asyncio.open_connection(self.addr, self.port)
        prompt = await read_from_stream(self.reader)
        if prompt is None:
            return False

        while True:
            name = input(prompt)
            if not await write_to_stream(self.writer, name):
                return False

            reply = await read_from_stream(self.reader)
            if reply is None:
                return False

            if reply == name:
                break

        return True

    async def load_history(self, chat_window: ChatWindow):
        num_messages = await read_from_stream(self.reader)
        if num_messages is None:
            return

        for _ in range(int(num_messages)):
            if message := await read_from_stream(self.reader):
                chat_window.add_message(message)
            else:
                return

    async def run(self, input_window: InputWindow, chat_window: ChatWindow):
        async def input_handler():
            while not self.stop_signal.is_set():
                input_window.refresh()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    message = await asyncio.get_event_loop().run_in_executor(
                        executor, input_window.get_input_message
                    )
                    if message in ["", "\n"]:
                        continue

                    if message == "exit":
                        self.stop_signal.set()
                        break

                    if not await write_to_stream(self.writer, message):
                        break

            print("exiting input handler")

        async def incoming_message_handler():
            while not self.stop_signal.is_set():
                if message := await read_from_stream(self.reader):
                    chat_window.add_message(message)

                else:
                    self.stop_signal.set()
                    break

            print("exiting message handler")

        await asyncio.gather(input_handler(), incoming_message_handler())
