import toupcam
import numpy as np
import pygame
from PIL import Image
import time
import os

toupcam.TOUPCAM_OPTION_RGB = 0
# TOUPCAM_OPTION_BINNING = 0x02

class App:
    def __init__(self):
        if not os.path.exists('check.txt'):
            print(f"Файл {'check.txt'} не найден. Создаю файл и заполняю данными...")
            # Открываем файл для записи и заполняем его данными
            with open('check.txt', "w") as file:
                data = ['0\n', '10000\n', '100']
                file.writelines(data)
                
        self.hcam = None
        self.buf = None
        self.total = 0
        self.img = None
        self.expotime = int(open('check.txt').readlines()[1].strip())
        self.gain = int(open('check.txt').readlines()[2].strip())
        self.last_time = time.time()
        self.frame_count = 0
        self.screen = None
        self.running = True
        self.width = 100
        self.height = 100

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                self.hcam.PullImageV4(self.buf, 0, 0, 0, None)
                self.total += 1
                
                self.set_variables()
                
                # print("Разрешение:", self.width, self.height)

                self.img = Image.frombuffer("RGB", (self.width, self.height), self.buf, "raw", "RGB", 0, 1)
                
                # self.img = np.frombuffer(self.buf, dtype=np.uint8).reshape((self.height, self.width, 3))



                self.update_image()
                if self.total % 50 == 0:
                    print(f"Image updated, total = {self.total}")
                    
                    print(self.img.mode)  # Должно быть 'I;16' для 16-битного grayscale
                    print(self.img.getextrema())  # Выведет min/max значения пикселей
                self.print_fps()
            except toupcam.HRESULTException as ex:
                print(f'Pull image failed, hr=0x{ex.hr & 0xffffffff:x}')

    def update_image(self):
        if self.img is not None and self.screen is not None:
            # Получаем размер экрана
            w, h = self.screen.get_size()

            if self.total % 50 == 0:
                print(f"Разрешение: {w}x{h}")

            # Создаем копию изображения, чтобы иметь доступ к его данным
            img_copy = self.img.copy()  # Создаем копию изображения

            # Ресайзим изображение
            pic = img_copy.resize((w, h), Image.Resampling.NEAREST)

            # Преобразуем изображение в байты для pygame
            img_surface = pygame.image.fromstring(pic.tobytes(), pic.size, pic.mode)
            self.screen.blit(img_surface, (0, 0))

            

    def start_gui(self):
        pygame.init()
        flags = pygame.RESIZABLE 
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        aspect_ratio = self.width / self.height

        pygame.display.set_caption('Просмотр изображения')
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        self.running = False
                        print('Program is exiting...')
                    
                    elif event.type == pygame.VIDEORESIZE:
                        new_width, new_height = event.size
                        
                        # Выравниваем по большей стороне
                        if new_width > new_height:
                            new_height = int(new_width / aspect_ratio)
                        else:
                            new_width = int(new_height * aspect_ratio)
                        
                        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                pygame.display.flip()
                
        except Exception as e:
            print(f"Error: {e}")

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            self.hcam = toupcam.Toupcam.Open(a[0].id)
            if self.hcam:
                try:
                    self.width, self.height = self.hcam.get_Size()
                    bufsize = toupcam.TDIBWIDTHBYTES(24 * self.width) * self.height
                    # bufsize = self.height * self.width * 4
                    print(f'Image size: {self.width} x {self.height}, bufsize = {bufsize}')
                    self.buf = bytes(bufsize)
                    if self.buf:
                        self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                        print('Camera started successfully')
                except Exception as e:
                    print(f'Unexpected error: {e}')
            else:
                print('Failed to open camera')
        else:
            print('No camera found')

    def close_camera(self):
        if self.hcam:
            self.hcam.Close()
            self.hcam = None

    def set_variables(self):
        self.setExpoTime(self.expotime)
        self.setGain(self.gain)
        self.setHZ(1) #0 - 60 герц, 1 - 50 герц
        # self.hcam.put_Binning(0x02, 'Average')
        

    def setExpoTime(self, expo):
        self.hcam.put_ExpoTime(expo)

    def setGain(self, gain):
        self.hcam.put_ExpoAGain(gain)
    
    def setHZ(self, hz):
        self.hcam.put_HZ(hz)

    def print_fps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_time
        if elapsed >= 1.0:
            fps = self.frame_count / elapsed
            print(f'FPS: {fps:.2f}')
            self.frame_count = 0
            self.last_time = current_time
    
    def takePhoto(self, fileName):
        if self.img:
            self.img.save(f'imgs/{fileName}.tiff')
            print(f'Image saved: imgs/image_{self.total}.tiff')
        else:
            print("Waiting for a valid image...")
    
    def saveTxt(self, fileName):
        image = self.img
        image_array = np.array(image)
        
        image_name = f'image{self.total}.txt'
        with open(image_name, "w") as f:
            f.write("[\n")
            for row in image_array:
                f.write("  " + str(row.tolist()) + ",\n")
            f.write("]\n")
        
        print("Успешный успех")

app = App()

def start_camera():
    app.run()
    app.start_gui()
