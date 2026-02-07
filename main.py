import asyncio


async def get_chat(domain, port):
    reader, writer = await asyncio.open_connection(domain, port)

    while True:
        line_text = await reader.readline()
        if not line_text:
            break

        print(line_text.decode().rstrip())


if __name__ == '__main__':
    asyncio.run(get_chat('minechat.dvmn.org', 5000))
