import re

def recognize_terms(text):
    """Recognize legal terms in the text"""
    legal_terms = {
        'Latin Terms': [
            'ad hoc', 'bona fide', 'de facto', 'prima facie', 'quid pro quo',
            'res ipsa loquitur', 'sine qua non', 'ultra vires'
        ],
        'Contract Terms': [
            'consideration', 'covenant', 'indemnification', 'liquidated damages',
            'specific performance', 'breach of contract', 'force majeure',
            'boilerplate', 'severability', 'entire agreement'
        ],
        'Legal Phrases': [
            'notwithstanding', 'heretofore', 'hereinafter', 'aforementioned',
            'pursuant to', 'in lieu of', 'subject to', 'provided that',
            'to the extent', 'mutatis mutandis'
        ]
    }
    
    found_terms = {}
    text_lower = text.lower()
    
    for category, terms in legal_terms.items():
        found_terms[category] = []
        for term in terms:
            if term.lower() in text_lower:
                found_terms[category].append(term)
    
    return found_terms

def get_term_definitions():
    """Get definitions for common legal terms"""
    definitions = {
        'consideration': 'Something of value exchanged between parties in a contract',
        'indemnification': 'Protection against financial loss or legal liability',
        'force majeure': 'Unforeseeable circumstances preventing contract fulfillment',
        'liquidated damages': 'Pre-agreed compensation for breach of contract',
        'severability': 'If one part of contract is invalid, rest remains enforceable',
        'bona fide': 'In good faith, genuine',
        'quid pro quo': 'Something for something, mutual exchange',
        'ultra vires': 'Beyond legal power or authority'
    }
    return definitions

def simplify_legal_terms(text):
    """Replace complex legal terms with simpler alternatives"""
    replacements = {
        'notwithstanding': 'despite',
        'heretofore': 'before this',
        'hereinafter': 'from now on',
        'aforementioned': 'mentioned above',
        'pursuant to': 'according to',
        'in lieu of': 'instead of',
        'mutatis mutandis': 'with necessary changes',
        'prima facie': 'at first sight',
        'sine qua non': 'essential requirement'
    }
    
    simplified_text = text
    for complex_term, simple_term in replacements.items():
        simplified_text = re.sub(
            r'\b' + re.escape(complex_term) + r'\b',
            simple_term,
            simplified_text,
            flags=re.IGNORECASE
        )
    
    return simplified_text
