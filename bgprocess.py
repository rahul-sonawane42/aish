import threading
import time
import zipfile
from datetime import datetime
import os


def cleanup_backup(backup_dest):
    r_days = 7
    cutoff_time = time.time() - (r_days * 86400)
    try:
        for filename in os.listdir(backup_dest):
            if not filename.endswith(".zip"):
                continue
            file_path = os.path.join(backup_dest, filename)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                except Exception:
                    pass
    except Exception:
        pass


def auto_backup(config_path, backup_dest):
    if not os.path.exists(backup_dest):
        os.makedirs(backup_dest)

    while True:
        time.sleep(1800)  # 30 mins

        if not os.path.exists(config_path):
            continue

        backup_dirs = []
        try:
            with open(config_path, "r") as f:
                for line in f.readlines():
                    clean_line = line.strip()
                    if clean_line and not clean_line.startswith("#"):
                        backup_dirs.append(clean_line)
        except Exception:
            continue

        if not backup_dirs:
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = os.path.join(backup_dest, f"backup_{timestamp}")
        try:
            with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as master_zip:
                for target_dir in backup_dirs:
                    target_dir = os.path.expanduser(target_dir)
                    if not os.path.exists(target_dir):
                        continue
                    folder_name = os.path.basename(os.path.normpath(target_dir))
                    for dirpath, dirnames, filenames in os.walk(target_dir):
                        for filename in filenames:
                            abs_path = os.path.join(dirpath, filename)
                            rel_path = os.path.relpath(abs_path, target_dir)
                            arcname = os.path.join(folder_name, rel_path)
                            master_zip.write(abs_path, arcname)
        except Exception:
            pass

        cleanup_backup(backup_dest)


def start_auto_backup(config_path, backup_dest):
    try:
        worker = threading.Thread(target=auto_backup, args=(config_path, backup_dest))
        worker.deamon = True
        worker.start()
        return True
    except Exception:
        return False
