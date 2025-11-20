import re

def detect_clauses(text):
    """Detect legal clauses in the text"""
    clauses = []
    
    # Split text into sentences
    sentences = re.split(r'[.!?]+', text)
    
    # Common clause patterns
    clause_patterns = [
        r'(?i)\b(whereas|hereby|therefore|shall|agreement|contract)\b.*',
        r'(?i)\b(liability|damages|breach|termination|indemnif)\w*\b.*',
        r'(?i)\b(force majeure|confidential|proprietary|warranty)\b.*',
        r'(?i)\b(party|parties).*\b(agree|obligat|responsible)\w*\b.*',
        r'(?i)\b(payment|fee|cost|expense)\w*\b.*',
        r'(?i)\b(intellectual property|copyright|trademark)\b.*'
    ]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue
            
        for pattern in clause_patterns:
            if re.search(pattern, sentence):
                clauses.append(sentence)
                break
    
    # Remove duplicates while preserving order
    unique_clauses = []
    for clause in clauses:
        if clause not in unique_clauses:
            unique_clauses.append(clause)
    
    return unique_clauses[:10]  # Return top 10 clauses

def classify_clause_type(clause):
    """Classify the type of legal clause"""
    clause_lower = clause.lower()
    
    if any(word in clause_lower for word in ['payment', 'fee', 'cost', 'price']):
        return 'Financial'
    elif any(word in clause_lower for word in ['liability', 'damages', 'breach']):
        return 'Liability'
    elif any(word in clause_lower for word in ['termination', 'end', 'expire']):
        return 'Termination'
    elif any(word in clause_lower for word in ['confidential', 'proprietary', 'secret']):
        return 'Confidentiality'
    elif any(word in clause_lower for word in ['intellectual property', 'copyright', 'patent']):
        return 'Intellectual Property'
    else:
        return 'General'
