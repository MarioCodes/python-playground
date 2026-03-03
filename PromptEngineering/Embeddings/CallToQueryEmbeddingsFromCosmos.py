"""We have a text that we want to be able to search into a vectorial database for similarity (CosmosDB)   
1st - we get the embeddings for 'text' with the SAME MODEL as the one used to upload the content into Cosmos DB
2nd - we search for proximity using the vectors and output the original text

Config:
    - embeddings model URL. This is the URL you get when you deploy the model in Azure Foundry
    - cosmosDB URL. This is the URL you get when you create the Cosmos DB instance in Azure
    - set EMBEDDINGS_API_KEY as system var
    - set COSMOSDB_KEY as system var
    - I run this through poetry with 'poetry run x'
"""
from sys import api_version
from openai import AzureOpenAI
from azure.cosmos import CosmosClient

import os

def createEmbeddingsForText(endpoint, key, text):
    client = AzureOpenAI(
        api_key=key,
        azure_endpoint=endpoint,
        api_version="2023-05-15",
        azure_deployment="text-embedding-3-large",
    )

    embedding = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )

    return embedding.data[0].embedding

def queryFromCosmosDB(db_endpoint, db_key, db_name, container_name, sow_query_embedding, top_k=5):
    container = CosmosClient(db_endpoint, credential=db_key).get_database_client(db_name).get_container_client(container_name)

    query = f"""
        SELECT TOP {top_k}
            c.id, 
            c.text, 
            c.embedding,
            VectorDistance(c.embedding, @query_vector) AS cosine_distance
        FROM c
        ORDER BY VectorDistance(c.embedding, @query_vector)
    """

    parameters = [
        {"name": "@query_vector", "value": sow_query_embedding}
    ]

    results = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return results

def main():
    # setup
    embeddings_model_url = "https://xxx.cognitiveservices.azure.com"
    cosmosdb_url = "https://xxx.documents.azure.com:443/"
    cosmosdb_key = os.environ.get('COSMOSDB_KEY')
    if not cosmosdb_key:
        print("Error: COSMOSDB_KEY environment variable is not set. Please set it before running the script.")
        return

    api_key = os.environ.get('EMBEDDINGS_API_KEY')
    if not api_key:
        print("Error: EMBEDDINGS_API_KEY environment variable is not set. Please set it before running the script.")
        return

    # create embeddings for the text
    text = "inu"

    vectors = createEmbeddingsForText(embeddings_model_url, api_key, text)
    print(f"Input text: '{text}'")

    # query from Cosmos DB using the embedding vector
    results = queryFromCosmosDB(cosmosdb_url, cosmosdb_key, "vectorial_ddbb_poc", "container_for_vectors", vectors, top_k=3)
    # Embeddings are a one-way transformation and cannot be reversed back into text
    # Instead, we store the original text alongside the embedding in Cosmos DB and retrieve it when querying for similar vectors
    print("Query results:")
    for result in results:
        print(f"  id: {result['id']}, text: '{result['text']}', cosine_distance: {result['cosine_distance']}")