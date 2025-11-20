import re
import string

def preprocess_text(text):
    """Preprocess text for analysis"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    # Normalize quotation marks
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()

def tokenize_sentences(text):
    """Split text into sentences"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def extract_keywords(text):
    """Extract potential legal keywords"""
    legal_keywords = [
        'agreement', 'contract', 'party', 'parties', 'shall', 'hereby',
        'whereas', 'therefore', 'obligation', 'liability', 'breach',
        'termination', 'clause', 'provision', 'indemnify', 'warranty',
        'damages', 'force majeure', 'confidential', 'proprietary'
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in legal_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords
