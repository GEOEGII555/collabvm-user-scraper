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
    args="${args} --no-user-group -G ${usergroup}" 
fi

adminargs="${args}"
if [ ! -z "${admingroup}" ]; then
    adminargs="${adminargs} -G ${admingroup}"
fi
guestargs="${args}"
if [ ! -z "${guestargs}" ]; then
    guestargs="${guestargs} -G ${guestgroup}"
fi

'''

def username_to_underscore_case(username: str) -> str:
    return username.lower().replace(" ", "_")

with open("users.json", "r") as f:
    users: set[User] = set([User.from_dict(x) for x in json.load(f)])

with open("funny_shell_script.sh", "w") as f:
    f.write(SHELL_SCRIPT_HEADER)
    f.write("\n")
    for user in users:
        x = username_to_underscore_case(user.username)
        if repr(x) not in [f'"{x}"', f"'{x}'"] or '"' in x or "'" in x:
            continue
        f.write(f'echo Adding user \\\"{x}\\\"... \\(Rank\\: {Rank.ELEMENTS[user.rank]}\\)\n')
        f.write("useradd ${")
        if user.rank == Rank.GUEST:
            f.write("guest")
        elif user.rank == Rank.USER:
            pass
        else:
            f.write("admin")
        f.write("args} ")
        f.write(x)
        f.write("\n")
    f.write("pause\n")
            