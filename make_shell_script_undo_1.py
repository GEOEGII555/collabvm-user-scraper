import json

from shared import User, Rank

SHELL_SCRIPT_HEADER = r'#!/bin/bash'.encode('utf-8')

def username_to_underscore_case(username: str) -> str:
    return username.lower().replace(" ", "_")

with open("users.json", "r") as f:
    users: set[User] = set([User.from_dict(x) for x in json.load(f)])

with open("undo_funny_shell_script.sh", "wb") as f:
    f.write(SHELL_SCRIPT_HEADER)
    f.write("\r\n".encode('utf-8'))
    for user in users:
        x = username_to_underscore_case(user.username)
        if repr(x) not in [f'"{x}"', f"'{x}'"] or '"' in x or "'" in x:
            continue
        f.write(f'echo Removing user \\\"{x}\\\"... \\(Rank\\: {Rank.ELEMENTS[user.rank]}\\)\r\n'.encode('utf-8'))
        f.write(f"userdel {x} --remove\r\n".encode('utf-8'))
        f.write(f"groupdel {x}\r\n".encode('utf-8'))
    f.write("pause\r\n".encode('utf-8'))