from threading import Thread
from checkFile import watch_file
from class_app import start_camera
import sys
import os
from datetime import datetime

if __name__ == '__main__':
    # Создадим директорию для логов, если её нет
    os.makedirs("logs", exist_ok=True)

    # Имя файла лога с датой (например: logs/app_2025-10-08.log)
    log_path = os.path.join("logs", f"app_{datetime.now():%Y-%m-%d %H:%M:%S}.log")

    # Открываем файл и перенаправляем stdout/stderr туда
    sys.stdout = open(log_path, "a", encoding="utf-8")
    sys.stderr = sys.stdout

    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] --- App started ---")

    watcher_thread = Thread(target=watch_file, daemon=True)
    watcher_thread.start()


    start_camera()

