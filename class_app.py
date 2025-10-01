import toupcam
import numpy as np
import pygame
from PIL import Image
import time
import funcs
import os
import cv2
import random
import json
import pyautogui
import os


class App:
    def __init__(self):
        self.hcam = None
        self.buf = None
        self.total = 0
        self.img = None
        # self.expotime = 10000
        # self.gain = 100
        self.last_time = time.time()
        self.screen = None
        self.running = True
        self.width = 100
        self.height = 100
        self.maxBit = 0
        data = funcs.readFile("settings.json", self.img, self.maxBit)
        
        # print(lines)
        self.expotime = data["exposition"]
        self.gain = data["gain"]
        self.binning = data["binning"]

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                self.hcam.PullImageV3(self.buf, 0, 0, 0, None)
                self.total += 1
                self.set_variables()
                if self.maxBit <= 8:
                    self.img = np.frombuffer(self.buf, dtype=np.uint8).reshape((self.height, self.width, 3))
                else:
                    self.img = np.frombuffer(self.buf, dtype=np.uint16).reshape((self.height, self.width, 3))

                self.update_image()
                # print(self.hcam.get_ExpoTime())
                # print(self.hcam.get_ExpoAGain())
            except toupcam.HRESULTException as ex:
                print(f'Pull image failed, hr=0x{ex.hr & 0xffffffff:x}')

    def start_gui(self):
        # Получаем размер экрана
        monitor_width, monitor_height = pyautogui.size()
        aspect_ratio = self.width / self.height

        pygame.init()

        # Полный экран без рамок
        flags = pygame.NOFRAME | pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((monitor_width, monitor_height), flags)
        pygame.display.set_caption('Просмотр изображения')

        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        self.running = False
                        self.close_camera()
                        print('Program is exiting...')

                # Обновление кадра
                self.update_image()

                pygame.display.flip()

        except Exception as e:
            print(f"Error: {e}")


    def update_image(self):
        if self.img is not None and self.screen is not None:
            screen_w, screen_h = self.screen.get_size()
            img_h, img_w, _ = self.img.shape
            img_aspect = img_w / img_h
            screen_aspect = screen_w / screen_h

            # Определяем масштаб
            if img_aspect > screen_aspect:
                # Ограничение по ширине
                new_w = screen_w
                new_h = int(screen_w / img_aspect)
            else:
                # Ограничение по высоте
                new_h = screen_h
                new_w = int(screen_h * img_aspect)

            # Ресайзим картинку
            resized = cv2.resize(self.img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

            # Ограничим до 1023 и переведем в 8-бит
            resized = np.clip(resized, 0, 2 ** self.maxBit)
            resized_8bit = ((resized / float(2 ** self.maxBit)) * 255).astype(np.uint8)

            # Конвертируем в PIL.Image
            img_pil = Image.fromarray(resized_8bit, mode='RGB')
            img_surface = pygame.image.fromstring(img_pil.tobytes(), img_pil.size, img_pil.mode)

            # Очистка экрана чёрным
            self.screen.fill((0, 0, 0))

            # Центрируем картинку
            x = (screen_w - new_w) // 2
            y = (screen_h - new_h) // 2
            self.screen.blit(img_surface, (x, y))


    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            self.hcam = toupcam.Toupcam.Open(a[0].id)

            if self.hcam:
                try:
                    
                    self.width, self.height = self.hcam.get_FinalSize()
                    
                    self.maxBit = self.hcam.MaxBitDepth()
                    # self.maxBit = 8
                    self.putOption()
                    
                    
            
                    # print("Final size -", self.width, self.height)
                    # print("Максимальная битность -", self.maxBit)

                    if self.maxBit <=8:
                        bufsize = int(self.height * self.width * 3)
                    else:
                        bufsize = int(self.height * self.width * 3 * 2)
                        
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
            time.sleep(1)
            start_camera()            
            
    def putOption(self):
        if self.maxBit <= 8: 
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_RAW, 0)
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BINNING, self.binning)
        else:
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_RGB, 1)
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BITDEPTH, 1)
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_RAW, 0)
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BINNING, self.binning)
            
        # print("Биннинг - ", self.binning)
        # self.hcam.put_Option(toupcam.TOUPCAM_OPTION_CG, 1)
        # print("put Option")
    
    def takePhotoByKey(self):
            # Теперь читаем файл
        with open("check.txt", 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file]
        lines[0] = 1
        lines[3] = random.randint(0, 10000)
        
        with open("check.txt", 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(f"{line}\n")
        
        # funcs.takePhoto(random.randint(0, 10000), self.img, self.maxBit)
            
    def close_camera(self):
        if self.hcam:
            self.hcam.Close()
            self.hcam.Stop()
            self.hcam = None

    def set_variables(self):
        self.setExpoTime(self.expotime)
        self.setGain(self.gain)
        self.setHZ(1)         

    def setExpoTime(self, expo):
        self.hcam.put_ExpoTime(int(expo))

    def setGain(self, gain):
        self.hcam.put_ExpoAGain(gain)
    
    def setHZ(self, hz):
        self.hcam.put_HZ(hz)

    def print_fps(self):
        current_time = time.time()
        elapsed = current_time - self.last_time
        if elapsed >= 1.0:
            fps = self.total / elapsed
            print(f'FPS: {fps:.2f}')
            self.total = 0
            self.last_time = current_time

app = App()

def start_camera():
    app.run()
    app.start_gui()
