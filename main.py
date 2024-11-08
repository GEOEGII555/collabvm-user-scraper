import asyncio
import time
import json
import logging
from typing import Optional

from websockets.client import connect

from shared import User

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)
logger = logging.getLogger()

def decode_message(msg: str) -> list[str]:
    result = []
    i = 0
    while True:
        if i >= len(msg):
            break
        if msg[i] == ';':
            break
        dotPosition = msg.find('.', i)
        length = int(msg[i:dotPosition])
        i = dotPosition + 1
        data = msg[i:i + length]
        i += length
        i += 1
        result.append(data)
    return result

def encode_message(msg: list[str]) -> str:
    return f"{','.join([f'{len(str(v))}.{str(v)}' for v in msg])};"

def get_origin_from_ws_url(ws_url: str) -> str:
    domain = ws_url.removeprefix("ws:").removeprefix("wss:").removeprefix("/").removeprefix("/").split("/", 1)[0]
    is_wss = ws_url.startswith("wss:")
    return f"http{'s' if is_wss else ''}://{domain}/"

async def fetch_users(ws_url: str, vm: Optional[str] = None) -> set[User]:
    users: set[User] = set[User]()
    if vm is None:
        logger.info(f"Fetching the VM list at {ws_url}...")
        startTime = time.time()
        vm_list = []
        async with connect(ws_url, subprotocols=['guacamole'], extra_headers=[["Origin", get_origin_from_ws_url(ws_url)]]) as websocket:
            await websocket.send(encode_message(['list']))
            while time.time() - startTime < 10:
                try:
                    message = decode_message(await asyncio.wait_for(websocket.recv(), 10))
                except asyncio.TimeoutError:
                    continue
                if message[0] == 'nop':
                    await websocket.send(encode_message(['nop']))
                if message[0] == 'list':
                    for i in range(1, len(message), 4):
                        vm_list.append(message[i])
                    await websocket.close()
                    break
        logger.info(f"VM list: {', '.join(vm_list)}")
        for vm in vm_list:
            users = users.union(await fetch_users(ws_url, vm))
        return users
    logger.info(f"Fetching the users list at {ws_url} in VM {vm}...")
    startTime = time.time()
    async with connect(ws_url, subprotocols=['guacamole'], extra_headers=[["Origin", get_origin_from_ws_url(ws_url)]]) as websocket:
        await websocket.send(encode_message(['connect', vm]))
        while time.time() - startTime < 10:
            try:
                message = decode_message(await asyncio.wait_for(websocket.recv(), 10))
            except asyncio.TimeoutError:
                continue
            if message[0] == 'nop':
                await websocket.send(encode_message(['nop']))
            if message[0] == 'adduser':
                for i in range(2, len(message), 2):
                    users.add(User(username=message[i], rank=int(message[i + 1])))
            if message[0] == 'rename':
                users.add(User(username=message[3], rank=int(message[4])))
    return users

def deduplicate_users_with_multiple_ranks(users: set[User]) -> set[User]:
    users_dict: dict[str, int] = dict[str, int]()
    for user in users:
        if user.username in users_dict.keys():
            users_dict[user.username] = max(users_dict[user.username], user.rank)
        else:
            users_dict[user.username] = int(user.rank)
    return set([User(username=x[0], rank=x[1]) for x in users_dict.items()])

async def main():
    logger.info("Starting to scrape all online users...")
    with open("servers.json", "r") as f:
        urls = json.load(f)
    with open("users.json", "r") as f:
        users = set([User.from_dict(x) for x in json.load(f)])
    orig_users = users.copy()
    results = await asyncio.gather(*[fetch_users(url) for url in urls], return_exceptions=True)
    for x in results:
        if isinstance(x, set):
            users = users.union(x)
    users = deduplicate_users_with_multiple_ranks(users)
    with open("users.json", "w") as f:
        json.dump([user.to_dict() for user in users], f)
    if orig_users == users:
        logger.info("No new users were added, and no existing users were updated.")
    elif len(orig_users) == len(users):
        logger.info("No new users were added, but some existing users were updated (happens when admins get a promotion).")
    else:
        logger.info(f"{len(users) - len(orig_users)} new users were added.")

if __name__ == '__main__':
    asyncio.run(main())