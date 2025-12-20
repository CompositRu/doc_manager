import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, jsonify, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config
from database import db, Document, Comment, Suggestion
from utils import extract_text, convert_docx_to_html, get_frequent_suggestions, update_suggestion
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Обработка favicon (чтобы избежать 404 ошибок)
@app.route('/favicon.ico')
def favicon():
    favicon_path = os.path.join(app.root_path, 'static', 'favicon.ico')
    if os.path.exists(favicon_path):
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')
    else:
        # Возвращаем 204 No Content если favicon нет
        return '', 204

# Главная страница
@app.route('/')
def index():
    active_tab = request.args.get('tab', 'documents')
    documents = Document.query.filter_by(is_deleted=False, parent_id=None).order_by(Document.date.desc()).all()
    suggestions = get_frequent_suggestions()
    today = datetime.today().strftime('%Y-%m-%d')
    
    return render_template('main.html', 
                         documents=documents,
                         suggestions=suggestions,
                         active_tab=active_tab,
                         today=today)

# Добавление документа
@app.route('/add', methods=['POST'])
def add_document():
    if 'file' not in request.files:
        flash('Нет файла для загрузки')
        return redirect(url_for('index', tab='add'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Не выбран файл')
        return redirect(url_for('index', tab='add'))
    
    # Сохранение файла
    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Извлечение текста для поиска (только для PDF и DOCX)
    full_text = extract_text(file_path) if file.filename.lower().endswith(('.pdf', '.docx')) else ""
    
    # Создание документа
    new_doc = Document(
        organization=request.form['organization'],
        department=request.form.get('department'),
        surname=request.form.get('surname'),
        date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
        doc_type=request.form['doc_type'],
        status='new',
        parent_id=request.form.get('parent_id') or None,
        filename=filename,
        file_path=file_path,
        full_text=full_text
    )
    
    db.session.add(new_doc)
    
    # Обновление подсказок
    update_suggestion('organization', request.form['organization'])
    if request.form.get('department'):
        update_suggestion('department', request.form['department'])
    
    db.session.commit()
    flash('Документ успешно добавлен')
    return redirect(url_for('index'))

# Просмотр документа в браузере
@app.route('/view/<int:doc_id>')
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Определение типа просмотра
    if doc.filename.lower().endswith('.pdf'):
        return render_template('viewer.html', doc=doc, content_type='pdf')
    elif doc.filename.lower().endswith('.docx'):
        content = convert_docx_to_html(doc.file_path)
        return render_template('viewer.html', doc=doc, content_type='docx', content=content)
    elif doc.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return render_template('viewer.html', doc=doc, content_type='image')
    else:
        # Для остальных типов предлагаем скачать
        return redirect(url_for('download_file', filename=doc.filename))

# Скачивание файла
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Поиск по содержимому
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index', tab='search'))

    # Ищем по ВСЕМ неудалённым документам (включая вложенные!)
    search_results = Document.query.filter(
        db.or_(
            Document.organization.ilike(f'%{query}%'),
            Document.department.ilike(f'%{query}%'),
            Document.surname.ilike(f'%{query}%'),
            Document.full_text.ilike(f'%{query}%')
        )
    ).filter_by(is_deleted=False).all()

    suggestions = get_frequent_suggestions()
    return render_template('search_results.html',  # ← новый шаблон!
                         documents=search_results,
                         suggestions=suggestions,
                         search_query=query)

# Удаление документа (в корзину)
@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    doc.is_deleted = True
    
    # Перемещение файла в папку корзины
    trash_path = os.path.join(app.config['UPLOAD_FOLDER'], 'trash', doc.filename)
    os.rename(doc.file_path, trash_path)
    doc.file_path = trash_path
    
    db.session.commit()
    flash('Документ перемещен в корзину')
    return redirect(request.referrer or url_for('index'))

# Восстановление из корзины
@app.route('/restore/<int:doc_id>', methods=['POST'])
def restore_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    doc.is_deleted = False
    
    # Возврат файла из корзины
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.filename)
    os.rename(doc.file_path, original_path)
    doc.file_path = original_path
    
    db.session.commit()
    flash('Документ восстановлен')
    return redirect(url_for('index', tab='trash'))

# Экспорт в Excel
@app.route('/export')
def export_excel():
    docs = Document.query.filter_by(is_deleted=False).all()
    
    data = [{
        'ID': d.id,
        'Организация': d.organization,
        'Подразделение': d.department or '',
        'Фамилия': d.surname or '',
        'Дата': d.date.strftime('%d.%m.%Y'),
        'Тип': 'Входящий' if d.doc_type == 'incoming' else 'Исходящий',
        'Статус': {
            'none': 'Без статуса',
            'new': 'Новый',
            'in_progress': 'В работе',
            'completed': 'Выполнен',
            'approved': 'Согласован',
            'rejected': 'Отклонен'
        }.get(d.status, d.status),
        'Файл': d.filename
    } for d in docs]
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Документы')
    output.seek(0)
    
    return send_file(output, download_name='documents_export.xlsx', 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Фильтрация документов
@app.route('/filter')
def filter_documents():
    org = request.args.get('organization')
    dept = request.args.get('department')
    doc_type = request.args.get('doc_type')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Document.query.filter_by(is_deleted=False)
    
    if org:
        query = query.filter(Document.organization.ilike(f'%{org}%'))
    if dept:
        query = query.filter(Document.department.ilike(f'%{dept}%'))
    if doc_type:
        query = query.filter_by(doc_type=doc_type)
    if status and status != 'all':
        query = query.filter_by(status=status)
    if start_date:
        query = query.filter(Document.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Document.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    documents = query.order_by(Document.date.desc()).all()
    suggestions = get_frequent_suggestions()
    
    return render_template('main.html', 
                         documents=documents,
                         suggestions=suggestions,
                         active_tab='documents',
                         filters_applied=True)

# API для получения подразделений по организации
@app.route('/api/departments/<organization>')
def get_departments(organization):
    # TODO: В будущем реализовать справочник подразделений
    # Пока возвращаем последние использованные подразделения для этой организации
    return jsonify([])

def init_app():
    """Инициализация приложения: создание директорий и БД"""
    # Создаем папку instance для базы данных
    os.makedirs(app.config.get('INSTANCE_FOLDER', 'instance'), exist_ok=True)

    # Создаем папки для загрузок
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'trash'), exist_ok=True)

    # Создаем таблицы в базе данных
    with app.app_context():
        db.create_all()
        print(f"✓ База данных: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"✓ Папка загрузок: {app.config['UPLOAD_FOLDER']}")

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000, debug=True)