import asyncio

from py_terminal_chat.utils import write_to_stream


class StreamWriterStore:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.writers: dict[str, asyncio.StreamWriter] = {}

    async def add(self, username: str, writer: asyncio.StreamWriter):
        async with self.lock:
            if self.writers.get(username, None) is None:
                self.writers[username] = writer
                return True

            return False

    async def remove(self, username: str):
        async with self.lock:
            del self.writers[username]

    async def broadcast(self, message: str):
        for writer in self.writers.values():
            if not await write_to_stream(writer, message):
                return False

        return True


class RecentMessageStore:
    def __init__(self, size: int):
        self.size = size
        self.recent_messages: list[str] = []
        self.lock = asyncio.Lock()

    async def add_message(self, message: str):
        async with self.lock:
            self.recent_messages.append(message)
            if len(self.recent_messages) > self.size:
                self.recent_messages.pop(0)

    async def send_all(self, writer: asyncio.StreamWriter):
        async with self.lock:
            await write_to_stream(writer, str(len(self.recent_messages)))

            for message in self.recent_messages:
                if not await write_to_stream(writer, message):
                    return False

        return True
