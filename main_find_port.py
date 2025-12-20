# main_find_port.py
# Вариант с автоматическим выбором свободного порта из списка
# Полезно для тестирования, когда стандартные порты могут быть заняты

import socket
import webbrowser
import time
import os
import sys
from app import app, init_app

def find_free_port_from_list(ports=[8080, 8000, 5000, 8888]):
    """Найти первый свободный порт из списка"""
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    # Если все заняты — взять любой свободный
    return find_free_port()

def find_free_port():
    """Найти любой свободный TCP-порт"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Система сама назначит свободный порт
        return s.getsockname()[1]

def get_base_dir():
    """Получить базовую директорию (для PyInstaller)"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    print("=" * 60)
    print("DocManager - Запуск с автовыбором порта")
    print("=" * 60)

    base_dir = get_base_dir()
    print(f"Базовая директория: {base_dir}")

    try:
        # Инициализация
        print("\n[1/4] Инициализация приложения...")
        init_app()
        print("✓ База данных и папки созданы")

        # Поиск свободного порта
        print("\n[2/4] Поиск свободного порта...")
        port = find_free_port_from_list()
        print(f"✓ Найден свободный порт: {port}")

        # Сохраняем порт в файл
        port_file = os.path.join(base_dir, "port.txt")
        with open(port_file, "w") as f:
            f.write(str(port))
        print(f"✓ Порт сохранен в {port_file}")

        # Открываем браузер
        print("\n[3/4] Открываем браузер...")
        time.sleep(1)
        webbrowser.open(f"http://127.0.0.1:{port}")

        # Запуск сервера
        print("\n[4/4] Запускаем сервер...")
        print("=" * 60)
        print(f"Сервер запущен на http://127.0.0.1:{port}")
        print(f"Для доступа из сети: http://<IP-адрес>:{port}")
        print("Нажмите Ctrl+C для остановки сервера")
        print("=" * 60)
        print()

        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print("\n" + "!" * 60)
        print("ОШИБКА ПРИ ЗАПУСКЕ:")
        print(str(e))
        print("!" * 60)
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
        sys.exit(1)