import asyncio


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

    async def broadcast(self, message: bytes):
        for writer in self.writers.values():
            writer.write(message)


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

    async def send_all(self, writer):
        async with self.lock:
            writer.write(f"{len(self.recent_messages)}\n".encode("utf-8"))
            for message in self.recent_messages:
                writer.write(f"{message}\n".encode("utf-8"))
