#!/usr/bin/env python3

import signal
import os
import shlex
import google.generativeai as genai
import warnings
from dotenv import load_dotenv
from pynput.keyboard import Key, Controller

GREEN = "\001\033[1;32m\002"
CYAN = "\001\033[1;36m\002"
RESET = "\001\033[0m\002"
banner = (
    GREEN
    + r"""
 █████╗ ██╗███████╗██╗  ██╗
██╔══██╗██║██╔════╝██║  ██║
███████║██║███████╗███████║
██╔══██║██║╚════██║██╔══██║
██║  ██║██║███████║██║  ██║
╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
"""
    + RESET
)

load_dotenv(".env")

warnings.filterwarnings("ignore", category=DeprecationWarning)
genai.configure(api_key=os.getenv("GEMINI_KEY"))
strict_rules = """
    You are the translation engine for a custom, minimalist Linux shell named AiSH.
Your ONLY job is to translate natural language into a single, executable shell command, or to converse/explain using ONLY the echo command.
CRITICAL RULES:
    STRICT FORMATTING: Output a raw command string and absolutely NOTHING ELSE. No markdown code blocks (```), no conversational filler (e.g., "Here is the command..."), no prefaces, and no suffixes.
    SINGLE LINE ONLY: Your entire output must exist on a single line. Do not use newline characters (\n).
    MUTUAL EXCLUSIVITY: Because AiSH does not support command chaining (&&, ||, ;), you cannot output an action command and an explanation at the same time.
        If the user requests an action, output ONLY the operational command (e.g., ls -la | grep txt).
        If the user asks a question, requests an explanation, or initiates conversation, output ONLY an echo command (e.g., echo "This command lists all text files.").
    CONVERSATION ENCAPSULATION: All dialogue, explanations, or non-actionable text MUST be wrapped in an echo "..." command using double quotes.
    ESCAPE CHARACTERS: When using echo "..." for conversation, you MUST properly escape any internal double quotes (\"), dollar signs (\$), or backticks (`) to prevent shell syntax errors.
    SHELL LIMITATIONS: AiSH only supports basic commands, pipes (|), and output redirection (>). Do NOT use &&, ||, ;, subshells (), or awk/sed scripts. Keep the logic entirely linear.
    SAFETY GUARDRAIL: If a request involves deleting system files, formatting drives, or executing any catastrophically dangerous action, DO NOT generate the command.
FALLBACK:
If a request violates any of these rules, is impossible, or is dangerous, you must output exactly:
echo "AiSH_ERROR: Cannot safely translate this request."
"""
model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=strict_rules)
chat = model.start_chat(history=[])

keyboard = Controller()


def handle_interrupt(signum, frame):
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


signal.signal(signal.SIGINT, handle_interrupt)


def ai_command(user_request):
    response = chat.send_message(user_request)

    return response.text.strip()


user = os.environ.get("USER", "user")

os.system("clear")
print(banner)


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
                    #               print(GREEN + "AiSH Security: " + RESET + "Blocked potentially destructive command.")
                    #                continue
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
            os.system("clear")
            os._exit(0)
        elif commlist[0] == "cd":
            try:
                if os.getcwd() == home and commlist[1] == "--":
                    os.chdir(os.environ["HOME"])
                elif len(commlist) == 1:
                    os.chdir(os.environ["HOME"])
                elif commlist[1] == "..":
                    os.chdir("../")
                else:
                    os.chdir(commlist[1])
            except Exception:
                print("No such directory")
                continue
        elif "|" in commlist:
            pipelist = comm.split("|")
            input_p = 0
            pids = []

            for i in range(len(pipelist)):
                is_last = i == len(pipelist) - 1
                if not is_last:
                    r, w = os.pipe()
                pid = os.fork()
                pids.append(pid)
                if pid == 0:
                    if input_p != 0:
                        os.dup2(input_p, 0)
                    if not is_last:
                        os.dup2(w, 1)
                        os.close(r)
                        os.close(w)

                    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                    cmd_args = shlex.split(pipelist[i])
                    try:
                        os.execvp(cmd_args[0], cmd_args)
                    except OSError:
                        print(cmd_args[0], ": command not found")
                    os._exit(1)
                else:
                    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                    if input_p != 0:
                        os.close(input_p)
                    if not is_last:
                        os.close(w)
                        input_p = r
            for p in pids:
                os.waitpid(p, 0)
        else:
            pid = os.fork()
            if pid == 0:
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                try:
                    if ">" in commlist:
                        try:
                            arrow_index = commlist.index(">")
                            file = open(commlist[arrow_index + 1], "w")
                            os.dup2(file.fileno(), 1)
                            commlist = commlist[:arrow_index]
                        except Exception as e:
                            print(e)
                            os._exit(0)
                    os.execvp(commlist[0], commlist)
                except OSError:
                    print(commlist[0], "is not a recognised command")
                os._exit(0)
            else:
                os.wait()


if __name__ == "__main__":
    main()
