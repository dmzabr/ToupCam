import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from class_app import app
import time
import funcs
import json


# Указываем путь к файлу, за которым будем следить
file_path = os.path.abspath("settings.json")
last_modified_time = 0  # Переменная для хранения времени последнего изменения

# Твоя функция, которая будет выполняться при изменении файла
def file_changed():
    global last_modified_time
    
    # Получаем текущее время изменения файла
    current_modified_time = os.path.getmtime(file_path)
    
    # Если изменение вызвано нашей же функцией, выходим
    if current_modified_time == last_modified_time:
        return
    
    # Обновляем время последнего изменения
    last_modified_time = current_modified_time
    
    data = funcs.readFile(file_path, app.img, app.maxBit)
    app.expotime = int(data['exposition'])
    app.gain = int(data['gain'])
    # app.binning = lines[4]

    # Даем немного времени системе обновить время изменения файла
    last_modified_time = os.path.getmtime(file_path)  # Обновляем время еще раз

# Создаем обработчик событий
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Проверяем, изменился ли именно наш файл
        if event.src_path == file_path:
            print(f"Обнаружено изменение в {event.src_path}")
            file_changed()

# Функция для запуска наблюдателя
def watch_file():
    folder_path = "imgs"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Папка 'imgs' создана.")
    else:
        print("Папка 'imgs' уже существует.")
        
    folder_path = "txts"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Папка 'txts' создана.")
    else:
        print("Папка 'txts' уже существует.")
        
    dir_to_watch = os.path.dirname(file_path)  # Берем папку, где лежит файл
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=dir_to_watch, recursive=False)  # Следим только за этой папкой
    observer.start()

    print(f"Следим за изменениями в файле: {file_path}")

    try:
        while True:
            time.sleep(1)  # Чтобы программа не завершалась
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

# Запуск наблюдателя
# if __name__ == "__main__":
#     watch_file(FILE_TO_WATCH)