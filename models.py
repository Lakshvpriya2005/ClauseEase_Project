from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    documents = db.relationship('Document', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    simplified_text = db.Column(db.Text, nullable=True)
    clauses = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def set_clauses(self, clauses_list):
        self.clauses = json.dumps(clauses_list)
    
    def get_clauses(self):
        if self.clauses:
            return json.loads(self.clauses)
        return []
