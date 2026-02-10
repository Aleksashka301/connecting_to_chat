import aiofiles
import argparse
import asyncio
import datetime
import logging

from environs import Env


async def authorization(domain, port):
    reader, writer = await asyncio.open_connection(domain, port)
    loop = asyncio.get_running_loop()

    response = await reader.readline()
    loger.info('sender: %s', response.decode().rstrip())

    token = await loop.run_in_executor(None, input)

    writer.write((token + '\n').encode())
    await writer.drain()
    loger.info('receiver: %s', token)

    if not token:
        response = await reader.readline()
        loger.info('sender: %s', response.decode().rstrip())

        nickname = await loop.run_in_executor(None, input)
        writer.write((nickname + '\n').encode())
        await writer.drain()
        loger.info('receiver: %s', nickname)

    return reader, writer


async def read_chat(domain, port, filename):
    reader, writer = await asyncio.open_connection(domain, port)

    while True:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line_text = await reader.readline()

        if not line_text:
            break

        decoded_message = line_text.decode().rstrip()

        async with aiofiles.open(filename, mode='a', encoding='utf-8') as file:
            await file.write(f'[{date}] {decoded_message}\n')

        loger.info(decoded_message)


async def write_chat(domain, port, token):
    reader, writer = await asyncio.open_connection(domain, port)
    loop = asyncio.get_running_loop()

    writer.write((token + '\n').encode())
    await writer.drain()

    while True:
        message = await loop.run_in_executor(None, input)
        writer.write((message + '\n\n').encode())
        await writer.drain()


async def main(domain, server_port, client_port, filename, token):
    await authorization(domain, server_port)

    await asyncio.gather(
        write_chat(domain, server_port, token),
        read_chat(domain, client_port, filename),
    )

if __name__ == '__main__':
    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', default=env.str('HOST'), help='Хост для подключения к чату'
    )
    parser.add_argument(
        '--server_port', default=env.int('SERVER_PORT'), help='Порт для подключения к чату'
    )
    parser.add_argument(
        '--client_port', default=env.int('CLIENT_PORT'), help='Порт для подключения к чату'
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

    asyncio.run(main(args.host, args.server_port, args.client_port, args.history, env.str('TOKEN')))
