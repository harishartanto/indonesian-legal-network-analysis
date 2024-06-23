import sys


def index_generated_topic(client, document_id, data):
    '''
    Index the generated topics and related information back to OpenSearch.

    Parameters:
    - client: The OpenSearch client instance.
    - document_id: The ID of the document to index.
    - data: The data to index.
    '''
    try:
        index_exists = client.indices.exists(index='produk_hukum_topik') # check if the index exists, if not create the index
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


def retrieve_doc(client, document_id, index_name, included_fields=None, excluded_fields=None):
    """
    Retrieve a document from an OpenSearch index based on its document ID.
    Optionally, include or exclude specific fields from the document source.

    Parameters:
    - client: The OpenSearch client instance.
    - document_id: The ID of the document to retrieve.
    - index_name: The name of the OpenSearch index.
    - included_fields: A list of fields to include in the document source (default is None).
    - excluded_fields: A list of fields to exclude from the document source (default is None).

    Returns:
    - document: The retrieved document source if found, otherwise None.
    """
    # Default to empty lists if included_fields or excluded_fields are not provided
    if included_fields is None:
        included_fields = []
    if excluded_fields is None:
        excluded_fields = []

    # Query body to retrieve document based on the document ID (Slug)
    query = {
        "query": {
            "match": {
                "Slug": document_id
            }
        },
        "_source": {
            "includes": included_fields,
            "excludes": excluded_fields
        }
    }

    try:
        # Execute the search query
        response = client.search(index=index_name, body=query)
        # Check if any documents were found
        if response['hits']['total']['value'] > 0:
            document = response['hits']['hits'][0]['_source']
        else:
            document = None

    except Exception as e:
        document = None
        print(f"Error retrieving document: {str(e)}", file=sys.stderr)

    return document