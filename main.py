import aiofiles
import argparse
import asyncio
import datetime
import json
import logging

from environs import Env


async def get_token(reader, writer):
    loop = asyncio.get_running_loop()
    response = await reader.readline()
    loger.info(response.decode().rstrip())

    token = await loop.run_in_executor(None, input)
    writer.write((token + '\n').encode())
    await writer.drain()

    response = await reader.readline()

    if token and response.decode().rstrip() == 'null':
        loger.info('server: Неизвестный токен. Проверьте его или зарегистрируйтесь заново.')
        return None

    if token:
        return token

    loger.info(f'server: {response.decode().rstrip()}')
    token = await registration(reader, writer)

    return token


async def registration(reader, writer):
    loop = asyncio.get_running_loop()
    nickname = await loop.run_in_executor(None, input)

    writer.write((nickname + '\n').encode())
    await writer.drain()
    loger.info(f'server: {nickname} присоединился к чату.')

    response = await reader.readline()
    response = response.decode().rstrip()

    return json.loads(response)['account_hash']


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


async def write_chat(reader, writer, token):
    loop = asyncio.get_running_loop()
    writer.write((token).encode())
    await writer.drain()

    response = await reader.readline()
    loger.info(response.decode().rstrip())

    while True:
        message = await loop.run_in_executor(None, input)
        writer.write((message + '\n\n').encode())
        await writer.drain()


async def main(domain, server_port, client_port, filename, token):
    reader, writer = await asyncio.open_connection(domain, server_port)

    try:
        if not token:
            token = await get_token(reader, writer)

        await asyncio.gather(
            write_chat(reader, writer, token),
            read_chat(domain, client_port, filename),
        )
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        default=env.str('HOST'),
        help='Хост для подключения к чату'
    )
    parser.add_argument(
        '--server_port',
        default=env.int('SERVER_PORT'),
        help='Порт для подключения к чату'
    )
    parser.add_argument(
        '--client_port',
        default=env.int('CLIENT_PORT'),
        help='Порт для подключения к чату'
    )
    parser.add_argument(
        '--history',
        default=env.str('HISTORY', default='history.txt'),
        help='Файл для сохранения истории переписки'
    )
    parser.add_argument(
        '--token',
        default=env.str('TOKEN', default=None),
        help='Токен для регистрации'
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

    loger.info('Соединение установлено!')

    asyncio.run(main(args.host, args.server_port, args.client_port, args.history, args.token))
