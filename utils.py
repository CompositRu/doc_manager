import os
import PyPDF2
from docx import Document
import mammoth

def extract_text(file_path):
    """Извлекает текст из PDF и DOCX файлов"""
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_path.lower().endswith('.docx'):
            doc = Document(file_path)
            return " ".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {str(e)}")
    return ""

def convert_docx_to_html(file_path):
    """Конвертирует DOCX в HTML для просмотра в браузере"""
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            return result.value
    except Exception as e:
        print(f"Error converting DOCX to HTML: {str(e)}")
        return "<p>Ошибка при отображении документа</p>"

def get_frequent_suggestions(limit=5):
    """Возвращает часто используемые организации и подразделения"""
    from database import Suggestion, db
    
    orgs = Suggestion.query.filter_by(entity_type='organization')\
        .order_by(Suggestion.usage_count.desc()).limit(limit).all()
    
    deps = Suggestion.query.filter_by(entity_type='department')\
        .order_by(Suggestion.usage_count.desc()).limit(limit).all()
    
    return {
        'organizations': orgs,
        'departments': deps
    }

def update_suggestion(entity_type, value):
    """Обновляет счетчик использования предложения"""
    from database import Suggestion, db
    from sqlalchemy.exc import IntegrityError

    suggestion = Suggestion.query.filter_by(
        entity_type=entity_type,
        value=value
    ).first()

    if suggestion:
        suggestion.usage_count += 1
    else:
        suggestion = Suggestion(entity_type=entity_type, value=value)
        db.session.add(suggestion)

    try:
        db.session.commit()
    except IntegrityError:
        # Race condition: запись уже создана другим процессом
        db.session.rollback()
        # Повторная попытка с обновлением существующей записи
        suggestion = Suggestion.query.filter_by(
            entity_type=entity_type,
            value=value
        ).first()
        if suggestion:
            suggestion.usage_count += 1
            db.session.commit()