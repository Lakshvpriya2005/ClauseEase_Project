ClauseEase — AI-powered Contract Simplifier.

Short description: ClauseEase extracts and simplifies legal clauses from PDF/DOCX files, highlights detected clauses and legal terms, and the users can download the report in txt format.<img width="1898" height="1053" alt="upload_document_page" src="https://github.com/user-attachments/assets/0c09889a-8e40-4490-9843-13562937f82c" />
<img width="1902" height="1021" alt="login_page" src="https://github.com/user-attachments/assets/d1d89945-5709-4c3e-882d-213444a55452" />
<img width="1900" height="1018" alt="home_page" src="https://github.com/user-attachments/assets/2071c134-4d36-4cfb-b760-6f5b3e377df2" />
<img width="686" height="1254" alt="contract_analysis_result" src="https://github.com/user-attachments/assets/178f5920-fcac-4675-9ac4-1d1ff2670495" />
<img width="1879" height="1004" alt="admin_panel_secure" src="https://github.com/user-attachments/assets/df183497-e58f-43bc-b7a2-f676e5b9b25e" />

## Key Features
- User registration / login.
- Upload PDF or DOCX documents.
- Automatic clause detection and legal-term recognition.
- Simplified plain-language version of the document.
- Simple visual analytics (word counts & clause summary charts).
- Download simplified result as a `.txt`.
- Admin dashboard (local-only access recommended) to view users & documents.
- History/logs for admin only (not shown to regular users)
## Project structure (simplified)
ClauseEase_Project/
│── app.py
│── models.py
│── requirements.txt
│── README.md
│── uploads/ # uploaded files (should be in .gitignore)
│── clauseease.db # sqlite DB (should be in .gitignore)
│── static/
│ ├── css/
│ ├── js/
│ ├── images/
│ └── screenshots/ # Put screenshots here (placeholders included)
│── templates/
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── upload.html
│ ├── analyze.html
│ └── admin_database.html
└── ai_modules/
├── document_ingestion.py
├── text_preprocessing.py
├── legal_clause_detection.py
├── legal_term_recognition.py
└── language_simplification.py

## Requirements
See `requirements.txt` in the repo. Example (already in your repo):
- Python 3.11 (recommended)
- Flask, Flask-Login, Flask-SQLAlchemy
- PyPDF2, python-docx
- matplotlib, seaborn, nltk, spacy
> Tip: Use a virtual environment: `python -m venv venv` → `.\venv\Scripts\activate` (Windows PowerShell) or `source venv/bin/activate` (macOS/Linux).
## 🚀 Setup & Run (Windows / VS Code)
1. Open VS Code and open the project folder.
2. Create & activate virtual environment (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
3. Install dependencies:
pip install -r requirements.txt
4. Download NLTK data used by the project:
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
5. Initialize DB & run:
# If your app creates DB automatically, just run:
python app.py
# or use Flask run if you set FLASK_APP:
# set FLASK_APP=app.py
# flask run
6. Open browser at http://127.0.0.1:5000/
Admin access & security (IMPORTANT):
The project includes a local admin flow used by the app.py script (example checks admin@clauseease.com in code).
Do not publish real admin credentials in the README or public repo.
Recommendation: Replace the hard-coded admin check in app.py with an environment-based secret or configure admin in the DB.
Example: ADMIN_EMAIL & ADMIN_PASSWORD from environment variables.
Admin routes are restricted in code to local requests (127.0.0.1) for safety.
Downloaded results:
The application produces a .txt simplified output (not PDF). Users can download that simplified text from the UI.
Added project screenshots

