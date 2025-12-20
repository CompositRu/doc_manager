from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    doc_type = db.Column(db.String(10), nullable=False)  # 'incoming'/'outgoing'
    status = db.Column(db.String(20), default='none')  # none, new, in_progress, completed, approved, rejected
    parent_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    full_text = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    
    parent = db.relationship('Document', remote_side=[id], backref='children')
    comments = db.relationship('Comment', back_populates='document', cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    document = db.relationship('Document', back_populates='comments')

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(20), nullable=False)  # 'organization' or 'department'
    value = db.Column(db.String(100), nullable=False, unique=True)
    usage_count = db.Column(db.Integer, default=1)