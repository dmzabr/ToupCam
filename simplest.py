import toupcam
import numpy as np
from tkinter import Tk, Label
from PIL import Image, ImageTk

class App:
    def __init__(self):
        self.hcam = None
        self.buf = None
        self.total = 0
        self.img = None  # Переменная для хранения изображения
        self.root = None  # Окно tkinter
        self.label = None  # Метка для отображения изображения

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                self.hcam.PullImageV3(self.buf, 0, 24, 0, None)
                self.total += 1
                self.hcam.put_ExpoTime(40000)

                # Преобразование буфера в изображение
                width, height = self.hcam.get_Size()
                image = np.frombuffer(self.buf, dtype=np.uint8).reshape((height, width, 3))
                self.img = Image.fromarray(image, 'RGB')

                if self.root and self.label:
                    self.update_image()

                print(f"Image updated, total = {self.total}")

            except toupcam.HRESULTException as ex:
                print('pull image failed, hr=0x{:x}'.format(ex.hr & 0xffffffff))
        else:
            print('event callback: {}'.format(nEvent))

    def update_image(self):
        """Обновляет изображение в окне tkinter."""
        if self.img:
            photo = ImageTk.PhotoImage(self.img)
            self.label.configure(image=photo)
            self.label.image = photo

    def start_gui(self):
        """Создает окно tkinter и запускает цикл."""
        self.root = Tk()
        self.root.title("Просмотр изображения")
        self.root.geometry("800x600")

        self.label = Label(self.root)
        self.label.pack(fill="both", expand=True)

        self.root.bind('<Return>', self.on_enter)
        self.root.mainloop()

    def on_enter(self, event):
        print("Program is exiting...")
        self.root.quit()

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            print('{}: flag = {:#x}, preview = {}, still = {}'.format(a[0].displayname, a[0].model.flag, a[0].model.preview, a[0].model.still))
            for r in a[0].model.res:
                print('\t = [{} x {}]'.format(r.width, r.height))

            self.hcam = toupcam.Toupcam.Open(a[0].id)
            if self.hcam:
                try:
                    width, height = self.hcam.get_Size()
                    bufsize = toupcam.TDIBWIDTHBYTES(width * 24) * height
                    print('image size: {} x {}, bufsize = {}'.format(width, height, bufsize))
                    self.buf = bytes(bufsize)
                    if self.buf:
                        try:
                            self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                            print("Camera started successfully")

                        except toupcam.HRESULTException as ex:
                            print('failed to start camera, hr=0x{:x}'.format(ex.hr & 0xffffffff))
                except Exception as e:
                    print(f"Unexpected error: {e}")
            else:
                print('failed to open camera')
        else:
            print('no camera found')

    def close_camera(self):
        if self.hcam:
            self.hcam.Close()
            self.hcam = None

    def take_photo(self):
        """Сохраняет текущее изображение в файл."""
        while True:
            if self.img:
                self.img.save(f'imgs/image_{self.total}.jpg')
                print(f'Image saved: imgs/image_{self.total}.jpg')
                break
            else:
                print("Waiting for a valid image...")

def take_photo():
    app = App()
    app.run()
    if app.hcam:
        app.take_photo()
        app.close_camera()

def start_camera(): 
    app = App()
    app.run()
    app.start_gui()
