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

def get_local_ip():
    """Получить локальный IP адрес"""
    import socket
    try:
        # Создаем UDP соединение (не отправляем данные)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def check_firewall_rule(port=8080):
    """Проверить наличие правила в брандмауэре Windows"""
    import subprocess
    import platform

    # Проверка только на Windows
    if platform.system() != 'Windows':
        return True  # На Linux/Mac не проверяем

    try:
        # Проверяем все возможные варианты имени правила
        rule_names = ['DocManager', 'DocManager Port 8080']

        for rule_name in rule_names:
            # Используем encoding с обработкой ошибок для Windows
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', f'name={rule_name}'],
                capture_output=True,
                encoding='cp866',  # Кодировка консоли Windows
                errors='ignore',   # Игнорировать ошибки декодирования
                timeout=5
            )

            # Если правило найдено и включено
            if result.returncode == 0:
                output = result.stdout
                # Проверяем наличие правила и порта
                if ('Enabled' in output or 'Yes' in output) and str(port) in output:
                    return True

        return False
    except Exception as e:
        # Если не удалось проверить - не пугаем пользователя
        print(f"  (Ошибка проверки: {e})")
        return None  # Неизвестно

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

        # Получаем IP адрес
        local_ip = get_local_ip()

        # Проверяем брандмауэр
        print("\n[2/4] Проверка брандмауэра...")
        firewall_ok = check_firewall_rule(8080)

        if firewall_ok is True:
            print("✓ Правило брандмауэра найдено - доступ из сети разрешён")
        elif firewall_ok is False:
            print("\n" + "!" * 70)
            print("⚠ ВНИМАНИЕ: Правило брандмауэра НЕ НАЙДЕНО!")
            print("!" * 70)
            print("Доступ из локальной сети ЗАБЛОКИРОВАН!")
            print()
            print("Для разрешения доступа:")
            print("  1. Правой кнопкой на setup_firewall.bat")
            print("     → Запуск от имени администратора")
            print()
            print("  ИЛИ в PowerShell (от админа) выполните:")
            print('     netsh advfirewall firewall add rule name="DocManager"')
            print('           dir=in action=allow protocol=TCP localport=8080')
            print("!" * 70)
            print()
        else:
            print("⚠ Не удалось проверить брандмауэр")

        # Открываем браузер автоматически
        print("\n[3/4] Открываем браузер...")
        time.sleep(1)  # Небольшая задержка перед открытием браузера
        webbrowser.open("http://127.0.0.1:8080")

        # Запускаем сервер
        print("\n[4/4] Запускаем сервер...")
        print("=" * 70)
        print("✓ Сервер запущен успешно!")
        print()
        print("📍 АДРЕСА ДЛЯ ПОДКЛЮЧЕНИЯ:")
        print(f"   Локально:     http://127.0.0.1:8080")
        print(f"   Из сети:      http://{local_ip}:8080")

        if firewall_ok is False:
            print()
            print("⚠ ВНИМАНИЕ: Доступ из сети заблокирован брандмауэром!")
            print("   Запустите setup_firewall.bat от администратора")

        print()
        print("Нажмите Ctrl+C для остановки сервера")
        print("=" * 70)
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