import time
import os
import numpy as np
import re
import cv2
from threading import Thread
from multiprocessing import Process
import json


def readFile(file_path, img, bits):
    # Если файл не существует, создаём его
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass  # Просто создаём пустой файл

    with open(file_path, "r") as read_file:
        data = json.load(read_file)
    
    # Если первая строка равна 1, делаем фото
    try:
        if int(data['isPhoto']) == 1:
            
            # print(lines)
            fileName = data['fileName']
            try:
                takePhoto(fileName, img, bits)
                saveTxt(fileName, img)
                    
                # pPhoto = Thread(target=takePhoto, args=(fileName, img, bits))
                # pTxt = Thread(target=saveTxt, args=(fileName, img))

                # pTxt.start()
                # pPhoto.start()

                print("Сделано фото")
                data['isPhoto'] = '0'
            except:
                print("Ошибка фотографии")
                data['isPhoto'] = '0'
    except:
        print('Ошибка: значение в поле "фото" должно быть 0 или 1')
        data['isPhoto'] = '0'
            
        # pTxt.join()
        # pPhoto.join()
        
    # Обновляем значение экспозиции
    try:
        expotime = int(data['exposition'])
    except:
        print("Ошибка: Значение выдержки не валидно")
        expotime = 10000
        data['exposition'] = f'{expotime}'
        
    try:
        gain = int(data['gain'])
    except:
        print("Ошибка: Значение усиления не валидно.")
        gain = 100
        data['gain'] = f'{gain}'
        
    try:
        binning = int(data['binning'])
        if binning < 1 or binning > 8:
            print("Ошибка: Значение биннинга должно быть от 0 до 8.")
            binning = 1
            data['binning'] = f'{binning}'
    except:
        print("Ошибка: Значение биннинга не валидно.")
        binning = 1
        data['binning'] = f'{binning}'

    # Записываем измененные строки обратно в файл
        
    saveFile(data, file_path)
    return(data)

def saveFile(data, file_path):
    try:
        with open(file_path, "w") as write_file:
            json.dump(data, write_file)
    except:
        time.sleep(0.1)
        with open(file_path, "w") as write_file:
            json.dump(data, write_file)
        
def takePhoto(fileName, img, bits):
    # Преобразуем изображение из RGB в BGR
    # img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Сделать 8 битное изображение
    img_normalized_16bit = np.clip(img * (65535 / (2 ** bits + 2)), 0, 65535).astype(np.uint16)


    # Сохраняем изображение
    cv2.imwrite(f'imgs/{fileName}.tiff', img_normalized_16bit)

def saveTxt(fileName, img):
    image_array = np.array(img)
    # print("Шейп:", image_array.shape)
    fileName = sanitizeFilename(fileName)
    image_name = f'txts/{fileName}.txt'
    
    
    with open(image_name, "w") as f:
        f.write("[\n")
        for row in image_array:
            f.write("  " + str(row.tolist()) + ",\n")
        f.write("]\n")
    
    print("Текстовый файл сохранен")
    
def sanitizeFilename(filename):
    replacement = '_'
    # Запрещенные символы для имен файлов в Windows и Linux
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F]'
    return re.sub(forbidden_chars, replacement, filename)