from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import shutil
from config import Config

# Создаем отдельное приложение и БД для корзины
from flask import Flask
trash_app = Flask(__name__)
trash_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{Config.TRASH_DATABASE_PATH}"
trash_db = SQLAlchemy(trash_app)

class TrashDocument(trash_db.Model):
    """
    Модель документа в корзине
    """
    id = trash_db.Column(trash_db.Integer, primary_key=True)
    original_id = trash_db.Column(trash_db.Integer, nullable=False)  # ID оригинального документа
    organization = trash_db.Column(trash_db.String(100), nullable=False)
    department = trash_db.Column(trash_db.String(100), nullable=True)
    surname = trash_db.Column(trash_db.String(100), nullable=True)
    date = trash_db.Column(trash_db.Date, nullable=False)
    tags = trash_db.Column(trash_db.String(200))
    filename = trash_db.Column(trash_db.String(200), nullable=False)
    doc_type = trash_db.Column(trash_db.String(20), nullable=True)
    parent_id = trash_db.Column(trash_db.Integer, nullable=True)  # ID родительского документа
    status = trash_db.Column(trash_db.String(20), nullable=True)
    content_text = trash_db.Column(trash_db.Text, nullable=True)
    comments = trash_db.Column(trash_db.Text, nullable=True)
    deleted_at = trash_db.Column(trash_db.DateTime, nullable=False, default=datetime.now)

def init_trash_db():
    """
    Инициализация БД корзины
    """
    with trash_app.app_context():
        trash_db.create_all()

def move_document_to_trash(document, original_id):
    """
    Перемещение документа в корзину
    """
    with trash_app.app_context():
        trash_doc = TrashDocument(
            original_id=original_id,
            organization=document.organization,
            department=document.department,
            surname=document.surname,
            date=document.date,
            tags=document.tags,
            filename=document.filename,
            doc_type=document.doc_type,
            parent_id=document.parent_id,
            status=document.status,
            content_text=document.content_text,
            comments=document.comments
        )
        trash_db.session.add(trash_doc)
        trash_db.session.commit()
        
        return trash_doc.id

def restore_document_from_trash(trash_doc_id):
    """
    Восстановление документа из корзины
    """
    with trash_app.app_context():
        trash_doc = TrashDocument.query.get_or_404(trash_doc_id)
        
        # Возвращаем файл из корзины в основную папку
        trash_file_path = os.path.join(Config.TRASH_FOLDER, trash_doc.filename)
        main_file_path = os.path.join(Config.UPLOAD_FOLDER, trash_doc.filename)
        
        if os.path.exists(trash_file_path):
            shutil.move(trash_file_path, main_file_path)
        
        # Удаляем запись из корзины
        trash_db.session.delete(trash_doc)
        trash_db.session.commit()
        
        return {
            'original_id': trash_doc.original_id,
            'organization': trash_doc.organization,
            'department': trash_doc.department,
            'surname': trash_doc.surname,
            'date': trash_doc.date,
            'tags': trash_doc.tags,
            'filename': trash_doc.filename,
            'doc_type': trash_doc.doc_type,
            'parent_id': trash_doc.parent_id,
            'status': trash_doc.status,
            'content_text': trash_doc.content_text,
            'comments': trash_doc.comments
        }

def get_trash_documents():
    """
    Получение всех документов из корзины
    """
    with trash_app.app_context():
        return TrashDocument.query.all()

def permanently_delete_from_trash(trash_doc_id):
    """
    Окончательное удаление документа из корзины
    """
    with trash_app.app_context():
        trash_doc = TrashDocument.query.get_or_404(trash_doc_id)
        
        # Удаляем файл из корзины
        file_path = os.path.join(Config.TRASH_FOLDER, trash_doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Удаляем запись из корзины
        trash_db.session.delete(trash_doc)
        trash_db.session.commit()