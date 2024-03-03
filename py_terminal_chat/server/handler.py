import asyncio
from py_terminal_chat.server.stores import StreamWriterStore, RecentMessageStore


class ClientHandler:
    def __init__(self, name: str, nhistory: int):
        self.name = name
        self.writers = StreamWriterStore()
        self.recent_messages = RecentMessageStore(nhistory)

    @staticmethod
    async def read_message(reader: asyncio.StreamReader) -> str | None:
        try:
            data = await reader.readline()
            return data.decode("utf-8").strip()
        except asyncio.IncompleteReadError as _:
            return None

    async def prompt_username(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while True:
            writer.write("Enter username: \n".encode("utf-8"))
            if (username := await self.read_message(reader)) is None:
                return None

            if username and await self.writers.add(username, writer):
                writer.write(f"{username}\n".encode("utf-8"))
                return username

            writer.write("Sorry, that username is taken.\n".encode("utf-8"))

    async def handle_connection(self, username: str, reader: asyncio.StreamReader):
        while True:
            if (message := await self.read_message(reader)) is None:
                await self.writers.remove(username)
                return

            message = f"{username}: {message} \n"
            await self.recent_messages.add_message(message)
            await self.writers.broadcast(message.encode("utf-8"))

    async def accept_connections(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writer.write(("Welcome to " + self.name + "\n").encode("utf-8"))
        await writer.drain()

        username = await self.prompt_username(reader, writer)
        if username is not None:
            await self.recent_messages.send_all(writer)
            await self.handle_connection(username, reader)

        print(f"User {username} has left the room")
        # await writer.drain()
        # await self.writers.broadcast(f"User {username} has left the room".encode("utf-8"))
