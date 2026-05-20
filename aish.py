#!/usr/bin/env python3

import readline
import atexit
import signal
import os
import shlex
from ui import GREEN, RESET, banner
from ai_engine import ai_command
from executor import run_command
from core_cmds import handle_bye, handle_cd
from completer import TabCompleter

signal.signal(signal.SIGINT, signal.SIG_IGN)

user = os.environ.get("USER", "user")

os.system("clear")
print(banner)
history_file = os.path.join(os.environ.get("HOME", "~"), ".aish_history")
try:
    readline.read_history_file(history_file)
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, history_file)

tab_completer = TabCompleter()

readline.set_completer(tab_completer.complete)

readline.parse_and_bind("tab: complete")


def main():
    while True:
        cwd = os.getcwd()
        home = os.environ["HOME"]
        cwd = cwd.replace(home, "~")

        topline = "╭─ " + user + "@AiSH ─ [" + cwd + "]"
        bottomline = "╰─❯ "
        prompt = GREEN + topline + "\n" + RESET + GREEN + bottomline + RESET
        comm = input(prompt)
        if comm.startswith("@ai "):
            try:
                nl = comm[4:]

                ai_suggest = ai_command(nl)

                dangerous_keywords = ["rm -rf", "mkfs", "dd ", "> /dev/sda"]

                is_dangerous = False
                for bad_word in dangerous_keywords:
                    if bad_word in ai_suggest:
                        is_dangerous = True
                        break

                if is_dangerous:
                    print(GREEN + "AI Suggests: " + RESET + ai_suggest)
                    confirm = input("Run command? [y/n]: ")
                    while confirm == "":
                        confirm = input("Enter choice. [y/n]: ")
                    if confirm.lower() == "y":
                        comm = ai_suggest
                        commlist = shlex.split(comm)
                    else:
                        print("Command Cancelled")
                        continue
                else:
                    comm = ai_suggest
                    commlist = shlex.split(comm)
            except Exception as e:
                print("AI Error: ", e)
                os._exit(1)
        else:
            commlist = shlex.split(comm)

        if not commlist:
            continue
        elif commlist[0] == "bye":
            handle_bye()
        elif commlist[0] == "cd":
            handle_cd(commlist)
        else:
            run_command(comm, commlist)


if __name__ == "__main__":
    main()
