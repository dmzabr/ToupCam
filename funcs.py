import time
# from class_app import app
import os
import numpy as np
import re
from PIL import Image
import tifffile
import imageio.v3 as iio
import cv2



file_path = os.path.abspath("check.txt")

def readFile(file_path, img):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # print(lines)
    
    if len(lines) != 4:
        print("Количество переменных lines:", len(lines))
        lines = ['0\n', '10000\n', '100\n', 'image']
    # Если первая строка равна 1, делаем фото
    if int(lines[0][0]) == 1:
        fileName = lines[3]
        # app.take_photo()
        # saveTxt(fileName)
        takePhoto(fileName, img)
        # saveTxt(fileName, img)
        # process = multiprocessing.Process(target=app.save_txt)
        # process.start()
        lines[0] = '0\n'
        print("Сделано фото")

    # Обновляем значение экспозиции
    try:
        expotime = int(lines[1])
    except:
        expotime = 10000
        lines[1] = expotime
        
    try:
        gain = int(lines[2])
    except:
        gain = 100
        lines[2] = gain

    # Записываем измененные строки обратно в файл
    saveFile(lines, file_path)
        
    print(expotime, gain)
    return([expotime, gain])

        
def saveFile(lines, file_path):
    try:
        with open(file_path, 'w') as f:
            f.writelines(lines)
    except:
        time.sleep(0,1)
        saveFile(lines)
        
def takePhoto(fileName, img):
    # Преобразуем изображение из RGB в BGR
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Нормализуем изображение в 16 бит
    img_normalized_16bit = np.clip(img_bgr * (65535 / 1024), 0, 65535).astype(np.uint16)

    # Сохраняем изображение
    cv2.imwrite(f'imgs/{fileName}.tiff', img_normalized_16bit)

def saveTxt(fileName, img):
    
    image = img
    image_array = np.array(image)
    print("Шейп:", image_array.shape)
    fileName = sanitize_filename(fileName)
    image_name = f'{fileName}.txt'
    
    
    with open(image_name, "w") as f:
        f.write("[\n")
        for row in image_array:
            f.write("  " + str(row.tolist()) + ",\n")
        f.write("]\n")
    
    print("Успешный успех")
    
def sanitize_filename(filename):
    replacement = '_'
    # Запрещенные символы для имен файлов в Windows и Linux
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F]'
    return re.sub(forbidden_chars, replacement, filename)