#!/usr/bin/env python3

import readline
import atexit
import signal
import os
import shlex
from ui import (
    OFF_WHITE,
    MUTED_BLUE,
    ERROR_RED,
    WARNING_YELLOW,
    AI_PURPLE,
    RESET,
    banner,
)
from ai_engine import ai_command
from executor import run_command
from core_cmds import handle_bye, handle_cd
from completer import TabCompleter
from bgprocess import start_auto_backup


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

    home = os.environ["HOME"]
    config_path = os.path.join(home, ".aish_backup.conf")
    backup_dest = os.path.join(home, ".aish_backups")

    if start_auto_backup(config_path, backup_dest):
        print(MUTED_BLUE + "Auto Backup ON" + RESET)
    else:
        print(ERROR_RED + "Auto Backup Error" + RESET)
    in_ai_session = False

    while True:
        cwd = os.getcwd()
        cwd = cwd.replace(home, "~")

        if in_ai_session:
            topline = f"╭─ {user}@AiSH ─ [{MUTED_BLUE}{cwd}{OFF_WHITE}] ─ [{AI_PURPLE} AI MODE{OFF_WHITE}]"
            bottomline = f"╰─{AI_PURPLE}❯{RESET} "
            prompt = OFF_WHITE + topline + "\n" + bottomline + RESET
        else:
            topline = f"╭─ {user}@AiSH ─ [{MUTED_BLUE}{cwd}{OFF_WHITE}]"
            bottomline = f"╰─{MUTED_BLUE}❯{RESET} "
            prompt = OFF_WHITE + topline + "\n" + bottomline + RESET

        comm = input(prompt)

        if not comm:
            continue

        if comm == "@ai":
            in_ai_session = True
            print(
                AI_PURPLE
                + "Activated AI Translation Mode. Type @endai to return to native shell."
                + RESET
            )
            continue

        if comm == "@endai":
            in_ai_session = False
            print(MUTED_BLUE + "Returned to Native Shell." + RESET)
            continue

        if comm == "@backup":
            config_file = os.path.expanduser("~/.aish_backup.conf")
            if not os.path.exists(config_file):
                with open(config_file, "w") as f:
                    f.write("""# ==========================================
# AiSH Backup Configuration
# ==========================================
# Add the absolute paths of the directories you want to back up.
# One directory path per line. 
# Empty lines and lines starting with '#' will be ignored.
# You can use '~' as a shortcut for your home directory.
#
# Examples:
# ~/Documents/MCA_Project
# /home/rahul/Downloads/important_pdfs
# ~/.config/nvim
# ==========================================

""")
            editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano"
            os.system(f"{editor} ~/.aish_backup.conf")

        if in_ai_session:
            try:
                nl = comm

                ai_suggest = ai_command(nl)

                dangerous_keywords = ["rm -rf", "mkfs", "dd ", "> /dev/sda"]

                is_dangerous = False
                for bad_word in dangerous_keywords:
                    if bad_word in ai_suggest:
                        is_dangerous = True
                        break

                if is_dangerous:
                    print(WARNING_YELLOW + "AI Suggests: " + RESET + ai_suggest)
                    confirm = input(WARNING_YELLOW + "Run command? [y/n]: " + RESET)
                    while confirm == "":
                        confirm = input("Enter choice. [y/n]: ")
                    if confirm.lower() == "y":
                        comm = ai_suggest
                        commlist = shlex.split(comm)
                    else:
                        print(ERROR_RED + "Command Cancelled" + RESET)
                        continue
                else:
                    if ai_suggest.startswith('echo "AiSH_ERROR'):
                        error_message = ai_suggest.split('"')[1]
                        print(ERROR_RED + error_message + RESET)
                        continue
                    comm = ai_suggest
                    commlist = shlex.split(comm)
            except Exception as e:
                error_msg = str(e).lower()
                if (
                    "429" in error_msg
                    or "quota" in error_msg
                    or "exhausted" in error_msg
                    or "limit" in error_msg
                ):
                    print(
                        ERROR_RED
                        + "AI Quota Reached: The translation engine is temporarily out of tokens."
                        + RESET
                    )
                else:
                    print(ERROR_RED + f"AI Network Error: {e}" + RESET)

                print(
                    MUTED_BLUE
                    + "Automatically returning to Native Shell Mode..."
                    + RESET
                )
                in_ai_session = False
                continue
        else:
            commlist = shlex.split(comm)

            if commlist and commlist[0] == "ls" and "--color=auto" not in commlist:
                commlist.insert(1, "--color=auto")

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
