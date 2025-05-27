from threading import Thread 
from checkFile import watch_file
from class_app import start_camera
from multiprocessing import Process


if __name__ == '__main__':
    watcher_thread = Process(target=watch_file)

    watcher_thread.daemon = True  
    watcher_thread.start()

    start_camera()
    watcher_thread.kill()
    


