# AiSH (AI Shell)

AiSH is a custom, multithreaded Unix shell written in Python. It bridges the gap between natural language and systems administration by integrating an AI translation layer directly into the command prompt.

Built with a decoupled, modular architecture, AiSH operates not just as a command executor, but as an autonomous system utility featuring detached background daemons, dynamic file routing, and a highly responsive user interface.

# Core Features

- AI Command Translation: Seamlessly translates natural language requests into executable Linux commands using an integrated AI engine.

- Autonomous Backup Daemon: A detached, asynchronous background thread that reads a self-documenting configuration file (~/.aish_backup.conf) and generates timestamped, compressed zip archives of your critical directories. It runs invisibly without blocking the main terminal prompt.

- Automated Garbage Collection: The background daemon actively monitors storage space, automatically purging backup archives older than 7 days to prevent disk overflow.

- Tab Autocompletion: Native integration with system readline libraries to provide instant path and directory autocompletion while typing.

- Modular Architecture: Clean separation of concerns. The AI engine, user interface, core commands, and background processes are isolated into dedicated modules for maximum stability and crash resistance.

# Installation

1. Clone the repository to your local machine:

    - git clone https://github.com/rahul-sonawane42/aish.git
    - cd aish

2. Ensure you have Python 3 installed on your system.
   - Install any required dependencies:
    - pip install -r requirements.txt

# Making AiSH Globally Executable

To run the shell simply by typing aish from anywhere in your terminal, you need to make the script executable and link it to your system's PATH.
- Step 1: Add the Shebang
  Open your main aish.py file and ensure the very first line of the file looks exactly like this. This tells your OS to use Python to run the file:

  - #!/usr/bin/env python3

- Step 2: Grant Execution Permissions
  Make the file an executable program:

  - chmod +x aish.py

- Step 3: Link to Your System Path
  Create a symbolic link to your local binaries folder. This allows the OS to find the program when you type aish.

  - ln -s $(pwd)/aish.py ~/.local/bin/aish

(Note: Ensure ~/.local/bin is in your shell's $PATH. If it is not, you can alternatively link it globally using sudo ln -s $(pwd)/aish.py /usr/local/bin/aish)

You can now open a new terminal window and simply type aish to boot the shell.
Configuration and Usage

# The Backup Engine

To configure the background backup daemon, launch AiSH and run the built-in trigger command:

-  @backup

This will automatically generate a ~/.aish_backup.conf file in your home directory with instructions and open it in your system's default text editor. Add the absolute paths of the directories you wish to back up, save, and exit. The background daemon will handle the rest autonomously.h
