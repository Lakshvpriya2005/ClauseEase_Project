import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Document
from ai_modules.document_ingestion import extract_text_from_file
from ai_modules.text_preprocessing import preprocess_text
from ai_modules.legal_clause_detection import detect_clauses
from ai_modules.legal_term_recognition import recognize_terms
from ai_modules.language_simplification import simplify_text
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from functools import wraps
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# 🔥 FIX DATABASE PATH ISSUE 🔥
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clauseease.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Template filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    if not s:
        return ''
    return s.replace('\n', '<br>')

@app.template_filter('safe_string')
def safe_string_filter(s):
    if not s:
        return ''
    return str(s).replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

# 🔥 FIXED DATABASE INITIALIZATION 🔥
def init_database():
    try:
        possible_paths = [
            'clauseease.db',
            os.path.join('instance', 'clauseease.db'),
            DATABASE_PATH
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                os.remove(path)
                print(f"✅ Removed old database: {path}")
        
        if os.path.exists('instance'):
            import shutil
            shutil.rmtree('instance')
            print("✅ Removed instance folder")
        
        db.create_all()
        print(f"✅ New database created at: {DATABASE_PATH}")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Tables created: {[t[0] for t in tables]}")
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

@login_manager.user_loader
def load_user(user_id):
    if str(user_id) == '999':
        class AdminUser:
            def __init__(self):
                self.id = 999
                self.username = 'admin'
                self.email = 'admin@clauseease.com'
                self.is_authenticated = True
                self.is_active = True
                self.is_anonymous = False
            def get_id(self):
                return str(self.id)
        return AdminUser()
    return User.query.get(int(user_id))

# 🔒 SECURE ADMIN DECORATOR 🔒
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
            flash('Access denied: Remote access blocked')
            return redirect(url_for('index'))
        
        user_agent = request.headers.get('User-Agent', '').lower()
        if not user_agent or 'bot' in user_agent or 'curl' in user_agent:
            flash('Access denied: Invalid client')
            return redirect(url_for('index'))
            
        if session.get('email') == 'admin@clauseease.com' and session.get('is_admin'):
            return f(*args, **kwargs)
            
        if current_user.is_authenticated and current_user.email == 'admin@clauseease.com':
            return f(*args, **kwargs)
            
        flash('Access denied: Admin only')
        return redirect(url_for('login'))
    return decorated_function

def get_admin_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# Initialize database
with app.app_context():
    init_database()

# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # 🎯 SIMPLE ADMIN ACCESS - PASSWORD: admin1234 🎯
        if email == 'admin@clauseease.com' and password == 'admin1234':
            if request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
                flash('❌ Admin access denied: Remote login blocked', 'error')
                return render_template('login.html')
            
            user_agent = request.headers.get('User-Agent', '').lower()
            if not user_agent or 'bot' in user_agent:
                flash('❌ Admin access denied: Invalid client', 'error')
                return render_template('login.html')
                
            print(f"🔐 Admin login at {datetime.now()}")
                
            session.clear()
            session['user_id'] = 999
            session['username'] = 'admin'
            session['email'] = 'admin@clauseease.com'
            session['is_admin'] = True
            session['admin_login_time'] = datetime.now().isoformat()
            
            class AdminUser:
                def __init__(self):
                    self.id = 999
                    self.username = 'admin'
                    self.email = 'admin@clauseease.com'
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False
                def get_id(self):
                    return str(self.id)
            
            admin_user = AdminUser()
            login_user(admin_user, remember=False)
            flash('🔓 Admin Access Granted!', 'success')
            return redirect(url_for('admin_database'))

        # Normal user check
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome {user.username}!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Wrong email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    if session.get('is_admin'):
        print(f"🔐 Admin logout at {datetime.now()}")
    session.clear()
    logout_user()
    flash('Logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('upload.html')

        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return render_template('upload.html')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                original_text = extract_text_from_file(filepath)
                preprocessed_text = preprocess_text(original_text)
                detected_clauses = detect_clauses(preprocessed_text)
                recognized_terms = recognize_terms(preprocessed_text)
                simplified_text = simplify_text(preprocessed_text)

                document = Document(
                    filename=filename,
                    user_id=current_user.id,
                    original_text=original_text,
                    simplified_text=simplified_text
                )
                document.set_clauses(detected_clauses)
                db.session.add(document)
                db.session.commit()

                generate_charts(original_text, simplified_text, detected_clauses, document.id)
                return redirect(url_for('analyze', doc_id=document.id))

            except Exception as e:
                flash(f'Error: {str(e)}')
                return render_template('upload.html')
        else:
            flash('Invalid file type. Use PDF or DOCX.')

    return render_template('upload.html')

@app.route('/analyze/<int:doc_id>')
@login_required
def analyze(doc_id):
    document = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()
    if not document:
        flash('Document not found')
        return redirect(url_for('upload'))
    return render_template('analyze.html', document=document)

@app.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    document = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()
    if not document:
        flash('Document not found')
        return redirect(url_for('upload'))

    output_filename = f"simplified_{document.filename.rsplit('.', 1)[0]}.txt"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Original: {document.filename}\n")
        f.write("="*50 + "\n\n")
        f.write("SIMPLIFIED:\n")
        f.write(document.simplified_text or 'No text')
        f.write("\n\n" + "="*50 + "\n")
        f.write("CLAUSES:\n")
        clauses = document.get_clauses()
        for i, clause in enumerate(clauses, 1):
            f.write(f"{i}. {clause}\n")

    return send_file(output_path, as_attachment=True, download_name=output_filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}

def generate_charts(original_text, simplified_text, clauses, doc_id):
    try:
        plt.style.use('default')
        original_words = len(original_text.split())
        simplified_words = len(simplified_text.split())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        categories = ['Original', 'Simplified']
        word_counts = [original_words, simplified_words]
        colors = ['#667eea', '#764ba2']

        bars1 = ax1.bar(categories, word_counts, color=colors, alpha=0.8)
        ax1.set_title('Word Count')
        ax1.set_ylabel('Words')

        for bar, count in zip(bars1, word_counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(word_counts)*0.01,
                     f'{count}', ha='center', va='bottom', fontweight='bold')

        clause_types = ['Clauses', 'Complex']
        clause_counts = [len(clauses), max(1, len(clauses) // 3)]
        colors2 = ['#f093fb', '#f5576c']

        bars2 = ax2.bar(clause_types, clause_counts, color=colors2, alpha=0.8)
        bars2.set_title('Analysis')
        ax2.set_ylabel('Count')

        for bar, count in zip(bars2, clause_counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(clause_counts)*0.01,
                     f'{count}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        chart_path = f'static/images/analysis_chart_{doc_id}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Chart error: {e}")

# 🔐 ADMIN ROUTES 🔐
@app.route('/admin/database')
@admin_required
def admin_database():
    try:
        conn = get_admin_db_connection()
        print(f"🔍 Admin database access at {datetime.now()}")
        
        try:
            users = conn.execute('SELECT * FROM user ORDER BY id DESC LIMIT 100').fetchall()
            print(f"📊 Found {len(users)} users")
        except Exception as e:
            print(f"❌ User query error: {e}")
            users = []
        
        try:
            documents = conn.execute('''
                SELECT d.*, u.username, u.email
                FROM document d
                LEFT JOIN user u ON d.user_id = u.id
                ORDER BY d.id DESC LIMIT 100
            ''').fetchall()
            print(f"📄 Found {len(documents)} documents")
        except Exception as e:
            print(f"❌ Document query error: {e}")
            documents = []
        
        user_count = len(users)
        document_count = len(documents)
        conn.close()
        
        return render_template('admin_database.html', 
                             users=users, 
                             documents=documents,
                             user_count=user_count,
                             document_count=document_count)
                             
    except Exception as e:
        flash(f'Database error: {str(e)}')
        print(f"❌ Admin database error: {e}")
        return render_template('admin_database.html', 
                             users=[], 
                             documents=[],
                             user_count=0,
                             document_count=0)

@app.route('/admin/api/users')
@admin_required
def api_get_users():
    try:
        conn = get_admin_db_connection()
        users = conn.execute('SELECT * FROM user ORDER BY id DESC').fetchall()
        conn.close()
        
        users_list = []
        for user in users:
            user_dict = dict(user)
            for key, value in user_dict.items():
                if value is None:
                    user_dict[key] = 'N/A'
            users_list.append(user_dict)
            
        return jsonify(users_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/documents')
@admin_required
def api_get_documents():
    try:
        conn = get_admin_db_connection()
        documents = conn.execute('''
            SELECT d.*, u.username, u.email as user_email
            FROM document d
            LEFT JOIN user u ON d.user_id = u.id
            ORDER BY d.id DESC
        ''').fetchall()
        conn.close()
        
        docs_list = []
        for doc in documents:
            doc_dict = dict(doc)
            for key, value in doc_dict.items():
                if value is None:
                    doc_dict[key] = 'N/A'
                elif key in ['original_text', 'simplified_text'] and len(str(value)) > 500:
                    doc_dict[key] = str(value)[:500] + '...'
            docs_list.append(doc_dict)
            
        return jsonify(docs_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add-demo-data-localhost-only')
def add_demo_data():
    if request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
        return 'Access denied', 403
        
    try:
        user1 = User(username='john_doe', email='john@example.com')
        user1.set_password('password123')
        
        user2 = User(username='jane_smith', email='jane@example.com')
        user2.set_password('password123')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        doc1 = Document(
            filename='legal_contract.pdf',
            user_id=user1.id,
            original_text='This comprehensive legal agreement contains various complex clauses and stipulations that govern the relationship between parties...',
            simplified_text='This is a simple contract between two parties...'
        )
        doc1.set_clauses(['Payment Terms', 'Liability Clause', 'Termination Clause', 'Force Majeure'])
        
        doc2 = Document(
            filename='service_agreement.docx',
            user_id=user2.id,
            original_text='The service provider shall deliver professional services in accordance with industry standards...',
            simplified_text='The service provider will do the work professionally...'
        )
        doc2.set_clauses(['Service Terms', 'Payment Schedule', 'Confidentiality'])
        
        db.session.add(doc1)
        db.session.add(doc2)
        db.session.commit()
        
        return '✅ Demo data added successfully! Check admin panel now.'
        
    except Exception as e:
        return f'❌ Error: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)
