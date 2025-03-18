import threading
from checkFile import watch_file
from class_app import start_camera


watcher_thread = threading.Thread(target=watch_file)
watcher_thread.daemon = True  
watcher_thread.start()

start_camera()