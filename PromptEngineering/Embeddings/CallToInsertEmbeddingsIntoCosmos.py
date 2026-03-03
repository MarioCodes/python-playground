"""We have a text and we want to create its embedding and upload BOTH the og text and the embedding into Cosmos DB
1st - creates embeddings for 'text'
2nd - create an item which holds both text and embedding values and upload it into Cosmos DB

Azure resources needed:
    - Azure Foundry with a deployed 'text-embedding-3-large' model
    - Cosmos DB instance with a database and a container 

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

def uploadToCosmosDB(endpoint, key, db_name, container_name, item):
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(db_name)
    container = database.get_container_client(container_name)

    try:
        response = container.upsert_item(item)
        print(f"Item uploaded successfully: {response}")
        return response
    except Exception as e:
        return f"Error uploading item: {e}"

def main():
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
    text = "A car travels alone in the highway during the night"
    vectors = createEmbeddingsForText(embeddings_model_url, api_key, text)
    print(f"Input text: '{text}'")
    # print(f"Embedding dimensions: {len(vector)}") # see embedding dimensions

    # save original text and its vectors into a class and upload to Cosmos DB
    item = {
        "id": "5", # manually do +1 to the last id in the Cosmos DB container (this is a POC after all)
        "text": text,
        "embedding": vectors
    }
    results = uploadToCosmosDB(cosmosdb_url, cosmosdb_key, db_name="vectorial_ddbb_poc",container_name="container_for_vectors", item=item)
