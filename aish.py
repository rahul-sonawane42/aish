#!/usr/bin/env python3

import readline
import atexit
import os
import shlex
from ui import (
    TEXT_MAIN,
    PRIMARY,
    ERROR,
    WARNING,
    ACCENT_AI,
    RESET,
    banner,
)
from ai_engine import ai_command
from executor import run_command
from core_cmds import handle_bye, handle_cd
from completer import TabCompleter
from bgprocess import start_auto_backup

user = os.environ.get("USER", "user")

os.system("clear")
print(banner)
history_file = os.path.join(os.environ.get("HOME", "~"), ".aish_history")
try:
    readline.read_history_file(history_file)
    readline.set_history_length(1000)
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
        print(ACCENT_AI + "Auto Backup ON" + RESET)
    else:
        print(ERROR + "Auto Backup Error" + RESET)
    in_ai_session = False

    while True:
        cwd = os.getcwd()
        cwd = cwd.replace(home, "~")

        if in_ai_session:
            topline = f"╭─ {user}@AiSH ─ [{PRIMARY}{cwd}{TEXT_MAIN}] ─ [{ACCENT_AI} AI MODE{TEXT_MAIN}]"
            bottomline = f"╰─{ACCENT_AI}❯{RESET} "
            prompt = TEXT_MAIN + topline + "\n" + bottomline + RESET
        else:
            topline = f"╭─ {user}@AiSH ─ [{PRIMARY}{cwd}{TEXT_MAIN}]"
            bottomline = f"╰─{PRIMARY}❯{RESET} "
            prompt = TEXT_MAIN + topline + "\n" + bottomline + RESET

        try:
            comm = input(prompt)
        except EOFError:
            print()
            handle_bye()

        except KeyboardInterrupt:
            print()
            continue

        if not comm:
            continue

        if comm == "@ai":
            in_ai_session = True
            print(
                ACCENT_AI
                + "Activated AI Translation Mode. Type @endai to return to native shell."
                + RESET
            )
            continue

        if comm == "@endai":
            in_ai_session = False
            print(ACCENT_AI + "Returned to Native Shell." + RESET)
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
            continue

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
                    print(WARNING + "AI Suggests: " + RESET + ai_suggest)
                    confirm = input(WARNING + "Run command? [y/n]: " + RESET)
                    while confirm == "":
                        confirm = input("Enter choice. [y/n]: ")
                    if confirm.lower() == "y":
                        comm = ai_suggest
                        commlist = shlex.split(comm)
                    else:
                        print(ERROR + "Command Cancelled" + RESET)
                        continue
                else:
                    if ai_suggest.startswith('echo "AiSH_ERROR'):
                        error_message = ai_suggest.split('"')[1]
                        print(ERROR + error_message + RESET)
                        continue

                    readline.add_history(ai_suggest)

                    comm = ai_suggest
                    commlist = shlex.split(comm)

            except KeyboardInterrupt:
                print(WARNING + "\nAI Translation Cancelled." + RESET)
                continue

            except Exception as e:
                error_msg = str(e).lower()
                if (
                    "429" in error_msg
                    or "quota" in error_msg
                    or "exhausted" in error_msg
                    or "limit" in error_msg
                ):
                    print(
                        ERROR
                        + "AI Quota Reached: The translation engine is temporarily out of tokens."
                        + RESET
                    )
                else:
                    print(ERROR + f"AI Network Error: {e}" + RESET)

                print(
                    PRIMARY + "Automatically returning to Native Shell Mode..." + RESET
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
            try:
                run_command(comm, commlist)
            except KeyboardInterrupt:
                print("\n")

        try:
            readline.write_history_file(history_file)
        except Exception:
            pass


if __name__ == "__main__":
    main()
