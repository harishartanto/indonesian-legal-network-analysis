import sys


def index_generated_topic(client, document_id, data):
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


def retrieve_doc(client, document_id, index_name):
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
        response = client.search(index=index_name, body=query)
        document = response['hits']['hits'][0]['_source']

    except Exception as e:
        print(f"Error retrieving documents: {str(e)}")
        document = None

    return document