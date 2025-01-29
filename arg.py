import argparse
from simplest import start_camera, take_photo

# Ваш код (например, класс App и другие функции) вставить сюда.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск программы с камерой.")
    parser.add_argument("action", choices=["take_photo", "start_camera"], help="Выберите действие: 'take_photo' для фото или 'start_camera' для просмотра.")
    
    args = parser.parse_args()

    if args.action == "take_photo":
        take_photo()
    elif args.action == "start_camera":
        start_camera()
