# main.py
import os
import sys
import webbrowser
import time
from app import app, init_app  # ваш основной Flask-файл

def get_base_dir():
    """Получить базовую директорию (для PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Запущено из exe
        return os.path.dirname(sys.executable)
    else:
        # Запущено из Python
        return os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    print("=" * 60)
    print("DocManager - Система управления документами")
    print("=" * 60)

    base_dir = get_base_dir()
    print(f"Базовая директория: {base_dir}")
    print(f"Python версия: {sys.version}")
    print(f"Запущено из exe: {getattr(sys, 'frozen', False)}")

    try:
        # Инициализация приложения
        print("\n[1/3] Инициализация приложения...")
        init_app()
        print("✓ База данных и папки созданы")

        # Открываем браузер автоматически
        print("\n[2/3] Открываем браузер...")
        time.sleep(1)  # Небольшая задержка перед открытием браузера
        webbrowser.open("http://127.0.0.1:8080")

        # Запускаем сервер
        print("\n[3/3] Запускаем сервер...")
        print("=" * 60)
        print("Сервер запущен на http://127.0.0.1:8080")
        print("Для доступа из сети: http://<IP-адрес>:8080")
        print("Нажмите Ctrl+C для остановки сервера")
        print("=" * 60)
        print()

        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        print("\n" + "!" * 60)
        print("ОШИБКА ПРИ ЗАПУСКЕ:")
        print(str(e))
        print("!" * 60)
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
        sys.exit(1)