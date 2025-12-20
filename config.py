import os
import sys

def get_base_dir():
    """Получить базовую директорию (работает с PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Запущено из exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Запущено из Python
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')

    # База данных в instance/
    INSTANCE_FOLDER = os.path.join(BASE_DIR, 'instance')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTANCE_FOLDER, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Папка для загрузок
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS = {'*'}  # Отключена валидация файлов