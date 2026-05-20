import os
import glob
import readline


class TabCompleter:
    def __init__(self):
        self.commands = [
            "cd",
            "bye",
            "ls",
            "pwd",
            "echo",
            "cat",
            "rm",
            "mkdir",
            "clear",
            "nvim",
            "vimtouch",
            "grep",
        ]

    def complete(self, text, state):
        buffer = readline.get_line_buffer()

        if " " not in buffer:
            matches = [cmd for cmd in self.commands if cmd.startswith(text)]

        else:
            pattern = text + "*" if text else "*"
            matches = glob.glob(pattern)

            matches = [m + "/" if os.path.isdir(m) else m for m in matches]
        try:
            return matches[state]
        except IndexError:
            return None
