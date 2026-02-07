import aiofiles
import argparse
import asyncio
import datetime
import logging

from environs import Env


async def get_chat(domain, port, filename):
    reader, writer = await asyncio.open_connection(domain, port)

    while True:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line_text = await reader.readline()

        if not line_text:
            break

        async with aiofiles.open(filename, mode='a', encoding='utf-8') as file:
            await file.write(f'[{date}] {line_text.decode().rstrip()}\n')

        loger.info(line_text.decode().rstrip())


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

    asyncio.run(get_chat(args.host, args.port, args.history))
