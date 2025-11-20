import re
from .legal_term_recognition import simplify_legal_terms

def simplify_text(text):
    """Simplify legal text for better understanding"""
    if not text:
        return ""
    
    # Start with legal term simplification
    simplified = simplify_legal_terms(text)
    
    # Replace complex sentence structures
    simplified = simplify_sentence_structure(simplified)
    
    # Replace complex words with simpler alternatives
    simplified = replace_complex_words(simplified)
    
    # Improve readability
    simplified = improve_readability(simplified)
    
    return simplified

def simplify_sentence_structure(text):
    """Simplify complex sentence structures"""
    
    # Replace passive voice patterns
    passive_patterns = [
        (r'(\w+)\s+shall be\s+(\w+ed)', r'\1 will be \2'),
        (r'is\s+required\s+to\s+be', 'must be'),
        (r'are\s+required\s+to', 'must'),
        (r'it\s+is\s+agreed\s+that', 'the parties agree that'),
    ]
    
    for pattern, replacement in passive_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Simplify conditional statements
    conditional_patterns = [
        (r'in\s+the\s+event\s+that', 'if'),
        (r'provided\s+that', 'if'),
        (r'subject\s+to\s+the\s+condition\s+that', 'if'),
        (r'on\s+the\s+condition\s+that', 'if'),
    ]
    
    for pattern, replacement in conditional_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def replace_complex_words(text):
    """Replace complex words with simpler alternatives"""
    word_replacements = {
        'utilize': 'use',
        'commence': 'start',
        'terminate': 'end',
        'subsequent': 'later',
        'prior': 'before',
        'obtain': 'get',
        'provide': 'give',
        'maintain': 'keep',
        'establish': 'set up',
        'determine': 'decide',
        'sufficient': 'enough',
        'additional': 'extra',
        'approximately': 'about',
        'demonstrate': 'show',
        'indicate': 'show',
        'substantial': 'large',
        'component': 'part',
        'constitute': 'make up',
        'endeavor': 'try',
        'facilitate': 'help',
        'implement': 'carry out',
        'modification': 'change',
        'notification': 'notice',
        'obligation': 'duty',
        'occurrence': 'event',
        'remuneration': 'payment'
    }
    
    for complex_word, simple_word in word_replacements.items():
        pattern = r'\b' + re.escape(complex_word) + r'\b'
        text = re.sub(pattern, simple_word, text, flags=re.IGNORECASE)
    
    return text

def improve_readability(text):
    """Improve overall readability of the text"""
    
    # Break long sentences
    sentences = re.split(r'[.!?]', text)
    improved_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Split very long sentences at logical break points
        if len(sentence) > 150:
            # Split at conjunctions
            parts = re.split(r'\s+(and|or|but|however|nevertheless)\s+', sentence)
            if len(parts) > 1:
                # Reconstruct with proper punctuation
                current_part = parts[0]
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        improved_sentences.append(current_part.strip())
                        current_part = parts[i+1]
                    else:
                        current_part += ' ' + parts[i]
                improved_sentences.append(current_part.strip())
            else:
                improved_sentences.append(sentence)
        else:
            improved_sentences.append(sentence)
    
    # Rejoin sentences
    improved_text = '. '.join(improved_sentences)
    
    # Clean up formatting
    improved_text = re.sub(r'\s+', ' ', improved_text)
    improved_text = re.sub(r'\s*\.\s*\.', '.', improved_text)
    
    return improved_text.strip()

def get_readability_score(text):
    """Calculate a simple readability score"""
    if not text:
        return 0
    
    words = text.split()
    sentences = len(re.findall(r'[.!?]+', text))
    
    if sentences == 0:
        return 0
    
    avg_sentence_length = len(words) / sentences
    
    # Simple scoring: lower is better (more readable)
    if avg_sentence_length <= 15:
        return 90  # Very readable
    elif avg_sentence_length <= 20:
        return 70  # Readable
    elif avg_sentence_length <= 25:
        return 50  # Somewhat readable
    else:
        return 30  # Difficult to read
