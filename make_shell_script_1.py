import json

from shared import User, Rank

SHELL_SCRIPT_HEADER = r'''#!/bin/bash
echo Enter the group to add the guests to, or leave blank to not add to any group.
read guestgroup
echo Enter the group to add ALL users to, or leave blank to create groups with the same name as the user.
read usergroup
echo Enter the group to add the admins to, or leave blank to not add to any group.
read admingroup
args="--create-home"
if [ ! -z "${usergroup}" ]; then
    args="${args} --no-user-group -G ${usergroup}";
fi

adminargs="${args}"
if [ ! -z "${admingroup}" ]; then
    adminargs="${adminargs} -G ${admingroup}";
fi
guestargs="${args}"
if [ ! -z "${guestargs}" ]; then
    guestargs="${guestargs} -G ${guestgroup}";
fi

'''.replace("\r\n", "\n").replace("\n", "\r\n").encode('utf-8')

def username_to_underscore_case(username: str) -> str:
    return username.lower().replace(" ", "_")

with open("users.json", "r") as f:
    users: set[User] = set([User.from_dict(x) for x in json.load(f)])

with open("funny_shell_script.sh", "wb") as f:
    f.write(SHELL_SCRIPT_HEADER)
    f.write("\r\n".encode('utf-8'))
    for user in users:
        x = username_to_underscore_case(user.username)
        if repr(x) not in [f'"{x}"', f"'{x}'"] or '"' in x or "'" in x:
            continue
        f.write(f'echo Adding user \\\"{x}\\\"... \\(Rank\\: {Rank.ELEMENTS[user.rank]}\\)\r\n'.encode('utf-8'))
        f.write("useradd ${".encode('utf-8'))
        if user.rank == Rank.GUEST:
            f.write("guest".encode('utf-8'))
        elif user.rank == Rank.USER:
            pass
        else:
            f.write("admin".encode('utf-8'))
        f.write("args} ".encode('utf-8'))
        f.write(x.encode('utf-8'))
        f.write("\r\n".encode('utf-8'))
    f.write("pause\r\n".encode('utf-8'))
            