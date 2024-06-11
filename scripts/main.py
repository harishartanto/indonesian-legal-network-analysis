import os
import sys
import json
import time
from query_neo4j import *
from query_opensearch import *
from doc_parser_json import *
from doc_parser_text import *
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