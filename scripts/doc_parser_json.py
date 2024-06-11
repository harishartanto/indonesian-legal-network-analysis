import sys


def get_doc_info(json_blocks):
    '''
    Get document information from the JSON blocks of a document.
    '''
    try:
        doc_title = json_blocks.get('Judul', '')
        doc_law_number = json_blocks.get('Nomor', '')
        doc_number = json_blocks.get('No', '')
        doc_year = json_blocks.get('Tahun', '')
        doc_status = json_blocks.get('Status', '')

        # create a dictionary with the document information
        document_info = {
            "doc_title": doc_title,
            "doc_law_number": doc_law_number,
            "doc_number": doc_number,
            "doc_year": doc_year,
            "doc_status": doc_status
        }

        return document_info
    
    except Exception as e:
        print(f"Error getting document information: {str(e)}", file=sys.stderr)
        return None


def get_doc_considerant(json_blocks):
    '''
    Get considerant from the JSON blocks of a document.
    '''
    try:
        for block in json_blocks.get('Blocks', []):
            if block.get('Ref') == 'menimbang' and block.get('Type') == 'KONSIDERAN':
                considerant_content = block.get('Content', '')
                break
    except Exception as e:
        print(f"Error getting considerant: {str(e)}", file=sys.stderr)

    return considerant_content


def get_doc_firstarticle(json_blocks):
    '''
    Get first article from the JSON blocks of a document.
    '''
    try:
        for block in json_blocks.get('Blocks', []):
            if block.get('Type') == 'CONTENT_PASAL' and block.get('Pasal') == 'pasal-1':
                    first_article = block.get('Content', '')
                    break
    except Exception as e:
        print(f"Error getting first article: {str(e)}", file=sys.stderr)

    return first_article


def get_doc_headers(json_blocks):
    '''
    Get header title from the JSON blocks of a document.
    '''
    headers = []
    try:
        for block in json_blocks.get('Blocks', []):
            if block.get('Context') not in headers and block.get('Context') != '' and block.get('Context') is not None:
                headers.append(block.get('Context'))
    except Exception as e:
        print(f"Error getting header title: {str(e)}", file=sys.stderr)

    return headers