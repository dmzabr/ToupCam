from threading import Thread
from checkFile import watch_file
from class_app import start_camera
import sys
import os
from datetime import datetime

if __name__ == '__main__':
    os.makedirs("logs", exist_ok=True)

    # Имя файла (лучше не использовать двоеточия в имени)
    log_path = os.path.join("logs", f"app_{datetime.now():%Y-%m-%d_%H-%M-%S}.log")

    # Открываем файл в построчно-буферизованном режиме
    log_file = open(log_path, "a", encoding="utf-8", buffering=1)

    # Перенаправляем stdout/stderr
    sys.stdout = log_file
    sys.stderr = log_file

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] --- App started ---", flush=True)

    watcher_thread = Thread(target=watch_file, daemon=True)
    watcher_thread.start()

    try:
        start_camera()
    except Exception as e:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ERROR: {e}", flush=True)
        raise
    finally:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] --- App finished ---", flush=True)
        log_file.close()
