import time
import os
import numpy as np
import re
import cv2
from threading import Thread
from multiprocessing import Process
import json


# def readFile(file_path, img, bits):
#     # Если файл не существует, создаём его
#     if not os.path.exists(file_path):
#         with open(file_path, 'w') as f:
#             pass  # Просто создаём пустой файл
#             safeData = {"fileName": "i am dima", "isPhoto": "0", "exposition": 1000, "gain": 100, "binning": 1}
#             saveFile(safeData, file_path)

#     with open(file_path, "r") as read_file:
#         data = json.load(read_file)
    
#     # Если первая строка равна 1, делаем фото
#     try:
#         if int(data['isPhoto']) == 1:
            
#             # print(lines)
#             fileName = data['fileName']
#             try:
#                 takePhoto(fileName, img, bits)
#                 saveTxt(fileName, img, bits)
                    
#                 # pPhoto = Thread(target=takePhoto, args=(fileName, img, bits))
#                 # pTxt = Thread(target=saveTxt, args=(fileName, img))

#                 # pTxt.start()
#                 # pPhoto.start()

#                 print("Сделано фото")
#                 data['isPhoto'] = '0'
#             except:
#                 print("Ошибка фотографии")
#                 data['isPhoto'] = '0'
#     except:
#         print('Ошибка: значение в поле "фото" должно быть 0 или 1')
#         data['isPhoto'] = '0'
            
#         # pTxt.join()
#         # pPhoto.join()
        
#     # Обновляем значение экспозиции
#     try:
#         expotime = int(data['exposition'])
#     except:
#         print("Ошибка: Значение выдержки не валидно")
#         expotime = 10000
#         data['exposition'] = f'{expotime}'
        
#     try:
#         gain = int(data['gain'])
#     except:
#         print("Ошибка: Значение усиления не валидно.")
#         gain = 100
#         data['gain'] = f'{gain}'
        
#     try:
#         binning = int(data['binning'])
#         if binning < 1 or binning > 8:
#             print("Ошибка: Значение биннинга должно быть от 0 до 8.")
#             binning = 1
#             data['binning'] = f'{binning}'
#     except:
#         print("Ошибка: Значение биннинга не валидно.")
#         binning = 1
#         data['binning'] = f'{binning}'

#     # Записываем измененные строки обратно в файл
        
#     saveFile(data, file_path)
#     return(data)

def saveFile(data, file_path):
    try:
        with open(file_path, "w") as write_file:
            json.dump(data, write_file)
    except:
        time.sleep(0.1)
        with open(file_path, "w") as write_file:
            json.dump(data, write_file)
        
def takePhoto(fileName, img, bits):
    if (f"{type(img)}" == "<class 'NoneType'>"):
        print("Скип картинки, тип НонТип", f"{type(img)}", "<class 'NoneType'>")
        return
    
    print("Не скип картинки, тип НонТип", f"{type(img)}", "<class 'NoneType'>")

    # Преобразуем изображение из RGB в BGR
    # img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Сделать 16 битное изображение
    img_normalized_16bit = np.clip(img * (65535 / (2 ** bits + 2)), 0, 65535).astype(np.uint16)

    # width, height, colors = img_normalized_16bit.shape

    # Сохраняем изображение
    cv2.imwrite(f'imgs/{fileName}.tiff', img_normalized_16bit)


def saveTxt(fileName, img, bits):
    
    if (f"{type(img)}" == "<class 'NoneType'>"):
        return
    # нормализация в 16-бит
    txt_normalized_16bit = np.clip(img * (65535 / (2 ** bits - 1)), 0, 65535).astype(np.uint16)

    image_array = np.array(txt_normalized_16bit)
    fileName = sanitizeFilename(fileName)
    param = np.array([image_array.shape[1], image_array.shape[0], bits])
    
    # print(param)

    # путь для сохранения
    os.makedirs("txts", exist_ok=True)
    txt_name = f'txts/{fileName}.txt'
    
    # image_array = np.hstack((param, image_array))

    # сохраняем как читаемый текст
    # np.savetxt(txt_name, image_array, fmt="%d")

    # сохраняем как raw (байты)
    flat = image_array.flatten().tolist()
    flat = np.hstack((param, flat))

    print(f"Сохранено: {txt_name}")
    
    # with open(image_name, "w") as f:
    #     # Сохраняем все значения в одну строку, разделённые пробелом
    #     f.write(flat_list2)
    
    print("Текстовый файл сохранен")
    
def saveRaw(rawName, img, bits):
    
    if (f"{type(img)}" == "<class 'NoneType'>"):
        return
    
     # нормализация в 16-бит
    txt_normalized_16bit = np.clip(img * (65535 / (2 ** bits - 1)), 0, 65535).astype(np.uint16)

    image_array = np.array(txt_normalized_16bit)
    rawName = sanitizeFilename(rawName)
    param = np.array([int(image_array.shape[1]), int(image_array.shape[0]), int(bits)])
    
    # print(param)

    # путь для сохранения
    os.makedirs("txts", exist_ok=True)
    raw_name = f'txts/{rawName}.raw'

    # сохраняем как raw (байты)
    flat = image_array.flatten()
    print(f"Расплющен:  {type(flat)}")
    flat = np.hstack((param, flat)).astype(np.uint16)
    print(f"Добавлены 3 значения в начало:  {type(flat)}")
    
    #  print(flat[0], flat[1], flat[2], flat[3], flat[4])
    
    flat.tofile(raw_name)

    print(f"Сохранено {raw_name}, размер {image_array.shape}")
    
    # with open(image_name, "w") as f:
    #     # Сохраняем все значения в одну строку, разделённые пробелом
    #     f.write(flat_list2)
    
    print("Текстовый файл сохранен")
    
# def saveTxt(fileName, img, bits):
    
#     img_normalized_16bit = np.clip(img * (65535 / (2 ** bits + 2)), 0, 65535).astype(np.uint16)

#     image_array = np.array(img)
#     fileName = sanitizeFilename(fileName)
#     image_name = f'txts/{fileName}.txt'
    
#     img_size = image_array.shape
    
    
#     # Расплющим массив в одну строку и преобразуем в список
#     flat_list = image_array.flatten().tolist()
#     flat_list2 = f"{img_size}" + " " + " ".join(map(str, flat_list))
    
#     with open(image_name, "w") as f:
#         # Сохраняем все значения в одну строку, разделённые пробелом
#         f.write(flat_list2)
    
#     print("Текстовый файл сохранен")


    
# def saveTxt(fileName, img):
#     image_array = np.array(img)
#     # print("Шейп:", image_array.shape)
#     fileName = sanitizeFilename(fileName)
#     image_name = f'txts/{fileName}.txt'
    
    
#     with open(image_name, "w") as f:
#         f.write("[\n")
#         for row in image_array:
#             f.write("  " + str(row.tolist()) + ",\n")
#         f.write("]\n")
    
#     print("Текстовый файл сохранен")
    
def sanitizeFilename(filename):
    replacement = '_'
    # Запрещенные символы для имен файлов в Windows и Linux
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F]'
    return re.sub(forbidden_chars, replacement, filename)

def makeDefaultSettings(file_path):
    with open(file_path, 'w') as f:
            pass  # Просто создаём пустой файл
            safeData = {"fileName": "photo_name", "isPhoto": "0", "exposition": 10000, "gain": 100, "binning": 1}
            saveFile(safeData, file_path)

def readFile(file_path, img, bits):
    # Если файл не существует, создаём его
    if not os.path.exists(file_path):
        makeDefaultSettings(file_path)
        
    try:
        with open(file_path, "r") as read_file:
            data = json.load(read_file)
    except:
        print("ошибка чтения setting.json. Создание по новой со стандартными значениями...")
        
    
    # Если первая строка равна 1, делаем фото

    if int(data['isPhoto']) == 1:
        
        # print(lines)
        fileName = data['fileName']

        takePhoto(fileName, img, bits)
        saveTxt(fileName, img, bits)
        saveRaw(fileName, img, bits)
            
        # pPhoto = Thread(target=takePhoto, args=(fileName, img, bits))
        # pTxt = Thread(target=saveTxt, args=(fileName, img))

        # pTxt.start()
        # pPhoto.start()

        print("Сделано фото")
        data['isPhoto'] = '0'

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