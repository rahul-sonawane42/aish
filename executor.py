import signal
import os
import shlex


def run_command(comm, commlist):
    if "|" in commlist:
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
