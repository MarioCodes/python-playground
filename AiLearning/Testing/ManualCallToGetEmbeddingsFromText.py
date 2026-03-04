"""Manual call to an embeddings model deployed in Azure Foundry.

Converts text to embeddings and prints the resulting vector.

Usage:
    replace {set_your_url_project_here} with the URL for your Azure Foundry - it needs to be the URL and KEY you get when deploying a model
    set EMBEDDINGS_API_KEY=<key> to a valid Foundry with a deployed 'text-embedding-3-large'
    poetry run call-to-embeddings-model
"""
from sys import api_version
from openai import AzureOpenAI
import os

def createEmbedding(endpoint, key, text):
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

def main():
    text = "The dog and the fox"
    api_key = os.environ.get('EMBEDDINGS_API_KEY')
    if not api_key:
        print("Error: EMBEDDINGS_API_KEY environment variable is not set. Please set it before running the script.")
        return

    vector = createEmbedding("https://xxx.cognitiveservices.azure.com", api_key, text)
    print(f"Embedding vector: {vector}")
    print(f"Input text: '{text}'")
    print(f"Embedding dimensions: {len(vector)}")