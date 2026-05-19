import os


def handle_bye():
    os.system("clear")
    os._exit(0)


def handle_cd(commlist):
    home = os.environ["HOME"]
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
