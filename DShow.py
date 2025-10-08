import cv2

# Открываем первую камеру (если не работает, попробуйте 1, 2 и т.д.)
cap = cv2.VideoCapture(0)

# Проверяем, открылась ли камера
if not cap.isOpened():
    print("Не удалось открыть камеру.")
    exit()

# Устанавливаем разрешение (по желанию)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Не удалось получить кадр.")
        break

    # Отображаем изображение
    cv2.imshow("Levenhuk M30", frame)

    # Выход по нажатию клавиши ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

