import asyncio

from py_terminal_chat.server.stores import (
    RecentMessageStore,
    StreamWriterStore,
    write_to_stream,
)
from py_terminal_chat.utils import read_from_stream


class ClientHandler:
    def __init__(self, name: str, nhistory: int):
        self.name = name
        self.writers = StreamWriterStore()
        self.recent_messages = RecentMessageStore(nhistory)

    async def prompt_username(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        while True:
            if not await write_to_stream(writer, "Enter Username: "):
                return None

            if (username := await read_from_stream(reader)) is None:
                return None

            if await self.writers.add(username, writer):
                if not await write_to_stream(writer, username):
                    return None

                print(f"An user with username: {username} has joined the room")
                return username

            if not await write_to_stream(writer, "Sorry, that username is taken."):
                return None

    async def handle_connection(self, username: str, reader: asyncio.StreamReader):
        while True:
            if (message := await read_from_stream(reader)) is None:
                await self.writers.remove(username)
                return

            message = f"{username}: {message}"
            print(f"--> {message}")
            await self.recent_messages.add_message(message)

            if not await self.writers.broadcast(message):
                return

    async def accept_connections(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        username = await self.prompt_username(reader, writer)
        if username is not None:
            await self.recent_messages.send_all(writer)
            await self.handle_connection(username, reader)

        print(f"User {username} has left the room")
