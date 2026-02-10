import aiofiles
import argparse
import asyncio
import datetime
import logging

from environs import Env


async def read_chat(reader, user_typing, filename):
    while True:
        if user_typing.is_set():
            await asyncio.sleep(1)
            continue

        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line_text = await reader.readline()

        if not line_text:
            break

        decoded_message = line_text.decode().rstrip()

        async with aiofiles.open(filename, mode='a', encoding='utf-8') as file:
            await file.write(f'[{date}] {decoded_message}\n')

        loger.info(decoded_message)


async def write_chat(token, user_typing):
    reader, writer = await asyncio.open_connection('minechat.dvmn.org', '5050')
    loop = asyncio.get_running_loop()

    writer.write((token + '\n').encode())
    await writer.drain()

    while True:
        user_typing.set()
        message = await loop.run_in_executor(None, input)
        writer.write((message + '\n\n').encode())
        await writer.drain()
        user_typing.clear()


async def main(domain, port, filename, token):
    reader, writer = await asyncio.open_connection(domain, port)
    user_typing = asyncio.Event()
    user_typing.clear()

    await asyncio.gather(
        write_chat(token, user_typing),
        read_chat(reader, user_typing, filename),
    )

if __name__ == '__main__':
    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', default=env.str('HOST'), help='Хост для подключения к чату'
    )
    parser.add_argument(
        '--port', default=env.int('PORT'), help='Порт для подключения к чату'
    )
    parser.add_argument(
        '--history', default=env.str('HISTORY'), help='Файл для сохранения истории переписки'
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format= u'[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    loger = logging.getLogger(__name__)
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(args.history, 'w', encoding='utf-8') as file:
        file.write(f'[{date}] Соединение установлено!\n')

    loger.info('Соединение установлено')

    asyncio.run(main(args.host, args.port, args.history, env.str('TOKEN')))
