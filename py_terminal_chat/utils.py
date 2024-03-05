import asyncio


async def read_from_stream(reader: asyncio.StreamReader) -> str | None:
    try:
        data = await reader.readline()
        return data.decode("utf-8").strip()
    except asyncio.IncompleteReadError as _:
        return None
    except Exception as err:
        print(f"error happened during listening, details: {repr(err)}")
        return None


async def write_to_stream(writer: asyncio.StreamWriter, msg: str):
    try:
        writer.write(f"{msg}\n".encode("utf-8"))
        await writer.drain()
        return True

    except Exception as err:
        print(f"exception happened during writing message, details: {repr(err)}")
        return False
