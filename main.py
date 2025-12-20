# main.py
import os
import webbrowser
from app import app  # ваш основной Flask-файл

if __name__ == '__main__':
    # Открываем браузер автоматически (если нужно)
    webbrowser.open("http://127.0.0.1:8080")
    # Запускаем сервер на нестандартном порту, чтобы избежать конфликтов
    app.run(host='0.0.0.0', port=8080, debug=False)