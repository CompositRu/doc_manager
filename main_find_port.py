# тестовый вариант, т.к. на целевых машинах хочется иметь предсказуемый порт,
# чтобы легко подключаться с других машин в=к серверу
 
import socket
import webbrowser
from app import app
import os

def find_free_port_from_list(ports=[8080, 8000, 5000, 8888]):
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    # Если все заняты — взять любой
    return find_free_port()

def find_free_port():
    """Найти свободный TCP-порт."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Система сама назначит свободный порт
        return s.getsockname()[1]

def get_exe_dir():
    return os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()

if __name__ == '__main__':
    port = find_free_port_from_list()
    print(f"Запуск сервера на порту: {port}")
    port_file = os.path.join(get_exe_dir(), "port.txt")
    with open(port_file, "w") as f:
        f.write(str(port))
    
    # Автоматически открыть браузер на этом порту
    webbrowser.open(f"http://127.0.0.1:{port}")
    
    # Запуск Flask-сервера на найденном порту
    app.run(host='0.0.0.0', port=port, debug=False)