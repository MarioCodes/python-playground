"""We have a text that we want to be able to search into a vectorial database for similarity (CosmosDB)   
1st - we get the embeddings for 'text' with the SAME MODEL as the one used to upload the content into Cosmos DB
2nd - we search for proximity using the vectors and output the original text

Config:
    - review the model used to embed the query "text-embedding-3-large" and check it is deployed in your Azure Foundry
    - set FOUNDRY_URL as system var. This is the URL you get when you deploy models in your Foundry
    - set FOUNDRY_KEY
    - set COSMOSDB_URL
    - set COSMOSDB_KEY

I run this through poetry with 'poetry run x'
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

def requireEnvVar(name):
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"{name} is not set")
    return value

def main():
    # setup
    foundry_url = requireEnvVar('FOUNDRY_URL')
    foundry_key = requireEnvVar('FOUNDRY_KEY')
    cosmosdb_url = requireEnvVar('COSMOSDB_URL')
    cosmosdb_key = requireEnvVar('COSMOSDB_KEY')

    # create embeddings for the text
    text = "Park"

    vectors = createEmbeddingsForText(foundry_url, foundry_key, text)
    print(f"Input text: '{text}'")

    # query from Cosmos DB using the embedding vector
    results = queryFromCosmosDB(cosmosdb_url, cosmosdb_key, "vectorial_ddbb_poc", "container_for_manual_querying", vectors, top_k=2)
    # Embeddings are a one-way transformation and cannot be reversed back into text
    # Instead, we store the original text alongside the embedding in Cosmos DB and retrieve it when querying for similar vectors
    print("Query results:")
    for result in results:
        print(f"  id: {result['id']}, text: '{result['text']}', cosine_distance: {result['cosine_distance']}")