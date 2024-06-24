import re

# definition pattern
DEFINITIONS_PATTERN = r'(?:adalah|merupakan|yang\s+selanjutnya\s+(?:disebut|disingkat))'
EXTRACT_DEFINITION = r'(?:adalah|merupakan)\s*(.*)$'
SENTENCE_PREDEFINITION = r'(.*?)(?:yang\s+selanjutnya\s+(?:disebut|disingkat)|adalah|merupakan)'
SHORT_TERM_REGEX = r'yang\s+selanjutnya\s+(?:disingkat|disebut)(.*?)(?:adalah|merupakan)'
SENTENCE_SPLITTER_REGEX = r'\b\d+\.\s*'
WHITESPACE_REGEX = r'\s+'
DEFINITIONS_MARKERS = r'(?:Dalam\s+(?:Peraturan\s+(?:Menteri\s+Keuangan|Pemerintah(?:\s+Pengganti\s+Undang-Undang)?|Presiden(?:\s+Pengganti\s+Undang-Undang)?|Undang-Undang(?:\s+Darurat)?|Daerah|Ketetapan\s+Majelis\s+Permusyawaratan\s+Rakyat|Badan|Lembaga|Bagan\/Lembaga)|Penetapan\s+Presiden|Keputusan\s+Presiden|Instruksi\s+Presiden)\s+ini,\s*)?yang\s+dimaksud\s+dengan'

# Lambda function to detect if the text contains a definition.
# Checks if the definition pattern matches the text using a regex.
# Returns True if there is a match, False otherwise.
detect_definition = lambda text: bool(re.search(DEFINITIONS_PATTERN, text, flags=re.IGNORECASE))
# Lambda function to extract the definition from the text.
# Searches for the definition pattern in the text using a regex.
# If there's a match, returns the extracted definition (first group of the search result) after stripping leading and trailing spaces.
# If there's no match, returns None.
extract_definition = lambda text: (match := re.search(EXTRACT_DEFINITION, text)) and match.group(1).strip()

# Function to detect definitions within the provided text and return a structured result. Source: https://github.com/Parser-Legal-Document-Kemenkeu/Parser-Legal-Document-Kemenkeu/blob/master/utils/structuring/structur_section_pembukaan.py
def detect_definitions_in_text(text):
    """
    Detects definitions within the provided text and returns a structured result.

    Args:
        text (str): The input text containing potential definitions.

    Returns:
        dict: A dictionary containing detected definitions with details.
    """
    # Split the text into sentences using a regex pattern for sentence splitting
    sentences = [sentence.strip() for sentence in re.split(SENTENCE_SPLITTER_REGEX, text) if sentence.strip()]
    # Initialize an empty dictionary to store the results
    result = {}
    # Iterate over each sentence to check for definitions
    for index, sentence in enumerate(sentences, start=0):
        # Normalize the whitespace in the sentence
        sentence = re.sub(WHITESPACE_REGEX, ' ', sentence)
        # Check if the current sentence contains a definition
        if detect_definition(sentence):
            # Extract the term being defined
            term = re.search(SENTENCE_PREDEFINITION, sentence)
            term = term.group(1).strip() if term else None
            # Extract the short term if it exists in the sentence
            short_term = re.search(SHORT_TERM_REGEX, sentence)
            short_term = short_term.group(1).strip() if short_term else None
            # Extract the definition part from the sentence
            definition = extract_definition(sentence)
            # Store the extracted details in the result dictionary
            result[f"Definisi-{index}"] = {
                "Text": sentence,  # Original sentence containing the definition
                "Term": term,  # Term being defined
                "ShortTerm": short_term,  # Short term, if any
                "Definition": definition,  # Extracted definition
                "Type": "DEFINITION"  # Type of the entry
            }
    return result


def get_doc_definitionterms(first_article_content):
    '''
    Get definition terms from the first article content.
    '''
    definition_terms = detect_definitions_in_text(first_article_content)
    terms = []
    for definition_index in definition_terms:
        if definition_terms[definition_index]['ShortTerm'] is not None:
            terms.append(definition_terms[definition_index]['ShortTerm'])
    return terms

def split_headingterms(heading_content, splitter):
    '''
    Split heading terms based on the splitter.
    '''
    separated_header_values = [subitem for item in heading_content for subitem in item.split(splitter)]
    unique_header_values = list(dict.fromkeys(separated_header_values))
    return unique_header_values