import os
import sys
import json
import time
import pandas as pd
from doc_keywords_parser import *
from dotenv import load_dotenv
from openai import AzureOpenAI
from opensearchpy import OpenSearch

# Load environment variables from .env file
load_dotenv()

# OpenSearch configuration
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT"))
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_TEXT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY_TEXT")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
GPT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

# Initialize OpenSearch client
opensearch_client = OpenSearch(
    hosts = [{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    http_auth = (OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
)

# Initialize Azure OpenAI client
azure_client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT,
    api_key = AZURE_OPENAI_KEY,
    api_version = AZURE_API_VERSION,
)

# Index name for the documents to retrieve from OpenSearch
document_index = 'produk_hukum_new'


def index_generated_topic(document_id, data, client=opensearch_client):
    '''
    Index the generated topics and related information back to OpenSearch.
    '''
    try:
        index_exists = client.indices.exists(index='produk_hukum_analysis') # check if the index exists, if not create the index
        if not index_exists: # create the index if it does not exist
            client.indices.create(
                index='produk_hukum_topik', 
                ignore=400 # ignore 400 to not raise exception if index already exists
            )  

        index_response = client.index(
            index='produk_hukum_topik',
            id=document_id, 
            body=data,
            op_type='index'
        )
        print(f"Data indexed successfully: {index_response}")

    except Exception as e:
        print(f"Error indexing data: {str(e)}", file=sys.stderr)


def retrieve_doc(open_search_client, document_id, index_name):
    """
    Retrieve documents from an OpenSearch index based on a query with the document ID.
    """
    # Query body to retrieve document based on the document ID (Slug)
    query = {
        "query": {
            "match": {
                "Slug": document_id
            }
        }
    }

    try:
        response = open_search_client.search(index=index_name, body=query)
        document = response['hits']['hits'][0]['_source']
        return document

    except Exception as e:
        print(f"Error retrieving documents: {str(e)}")
        return None


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


def get_doc_definitionterms(first_article_content):
    '''
    Get definition terms from the first article content.
    '''
    definition_terms = DetectDefinitionsInText(first_article_content)
    terms = []
    if definition_terms:
        for term in definition_terms:
            if term['Term'] is not None:
                terms.append(term['Term'])
    
    return terms


def get_doc_topics(doc_title, considerant_content, model=GPT_MODEL, temperature=0.5, top_p=0, max_tokens=500):
    '''
    Get topics from the considerant content.
    '''
    prompt_path = os.path.join(os.path.dirname(__file__), 'data\\prompt', 'generation.txt')
    prompt = open(prompt_path, 'r').read().format(doc_title=doc_title, doc_consideration=considerant_content)

    response = azure_client.chat.completions.create(
        model = model,
        temperature = float(temperature),
        top_p = float(top_p),
        max_tokens = int(max_tokens),
        messages = [
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.choices[0].message.content


def topics_extraction(document_id, client=opensearch_client, document_index=document_index):
    '''
    Extract topics from the document and index the generated topics in OpenSearch.
    '''
    try:
        # retrieve document & extract related information and content from the document
        doc = retrieve_doc(client, document_id, document_index)
        doc_info = get_doc_info(doc)
        doc_considerant = get_doc_considerant(doc)
        doc_firstarticle = get_doc_firstarticle(doc)
        
        # extract keywords from the document json blocks
        doc_headers = get_doc_headers(doc)
        doc_definitionterms = get_doc_definitionterms(doc_firstarticle)

        # join headers and definition terms list 
        keywords = doc_headers + doc_definitionterms
        keywords = [keyword.lower() for keyword in keywords] # lowercase all keywords.

        # extract topics from the document considerant
        doc_topics = get_doc_topics(doc_info['doc_title'], doc_considerant) # the result is a string and each topic is separated by ";". The last topic has a dot (.) at the end.
        doc_topics = doc_topics.lower().split(";") # transform doc_topics to list (split by ";") and lowercase all topics.
        doc_topics = [topic.strip() for topic in doc_topics] # remove leading and trailing whitespaces from each topic.
        doc_topics[-1] = doc_topics[-1].replace(".", "") # remove dot (.) from the last element of the topics list.

        # result in dictionary/json format
        result = {
            "Judul": doc_info['doc_title'],
            "Nomor": doc_info['doc_law_number'],
            "No": doc_info['doc_number'],
            "Tahun": doc_info['doc_year'],
            "Status": doc_info['doc_status'],
            "Kata Kunci": keywords,
            "Topik": doc_topics,
        }

    except Exception as e:
        print(f"Error extracting topics: {str(e)}", file=sys.stderr)
        result = None

    return result
    

if __name__ == "__main__":
    start_time = time.time()

    output_path = os.path.join(os.path.dirname(__file__), 'data', 'output')
    document_id = sys.argv[1]
    result = topics_extraction(document_id)

    index_generated_topic(document_id, result)

    if result:
        json_result = json.dumps(result, indent=4)
        with open(f"{output_path}\\{document_id}_topics.json", 'w') as f:
            f.write(json_result)

        print(f"Result saved to {output_path}\\{document_id}_topics.json")
    else:
        print("Topics extraction failed.")

    end_time = time.time()
    execution_time = (end_time - start_time)
    print(f"Execution time: {execution_time:.2f} seconds")