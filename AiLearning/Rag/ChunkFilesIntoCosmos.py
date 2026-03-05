"""We have a knowledge base which we want to get the vectors for it and upload BOTH the og text and the vectors into Cosmos DB
1st - read files and chunk them
2nd - clean up the text of the chunks
3rd - create embeddings for the chunks in batches (to reduce API round-trips)
4rth - insert into Cosmos DB both the original text and the embedding vector for each chunk, as a single item

Azure resources needed:
    - Azure Foundry with a deployed 'text-embedding-3-large' model
    - Cosmos DB instance with a database and a container 

Config:
    - review the folder set to hold the knowledge base: "./Rag/knowledge_files/"
    - review the model used for embeddings "text-embedding-3-large" and check it is deployed in your Azure Foundry
    - set FOUNDRY_URL as system var. This is the URL you get when you deploy models in Azure Foundry
    - set FOUNDRY_KEY
    - set COSMOSDB_URL
    - set COSMOSDB_URL
    - set COSMOSDB_KEY

I run this through poetry with 'poetry run x'
"""
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
from datetime import datetime

def createEmbeddingsClient(endpoint, key):
    return AzureOpenAI(
        api_key=key,
        azure_endpoint=endpoint,
        api_version="2023-05-15",
        azure_deployment="text-embedding-3-large",
    )

def createEmbeddingsBatch(client, texts):
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-large"
    )
    return [item.embedding for item in response.data]

def getCosmosContainer(endpoint, key, db_name, container_name):
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(db_name)
    return database.get_container_client(container_name)

def uploadToCosmosDB(container, item):
    try:
        container.upsert_item(item)
    except Exception as e:
        return f"Error uploading item: {e}"

def requireEnvVar(name):
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"{name} is not set")
    return value

# TODO: check and think how to check if documents have already been uploaded to CosmosDB. I need to avoid duplicates and stale information
def main():
    foundry_url = requireEnvVar('FOUNDRY_URL') 
    foundry_key = requireEnvVar('FOUNDRY_KEY')
    cosmosdb_url = requireEnvVar('COSMOSDB_URL')
    cosmosdb_key = requireEnvVar('COSMOSDB_KEY')

    # load all PDFs we want to use for the RAG
    
    # this retrieves all PDFs, each page as its own document
    loader = PyPDFDirectoryLoader("./Rag/knowledge_files/")
    docs = loader.load()
    if not docs:
        print("Error: No documents found in the specified directory. Please add some PDF files to './Rag/knowledge_files/' and try again.")
        return

    print(f"\nTOTAL DOCUMENTS LOADED: {len(docs)}\n")
    for doc in docs:
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        print(f"Document: {source} (page {doc.metadata.get('page', '?')+1})")
        print("Raw document's content:")
        print(f"{repr(doc.page_content)}\n")

    # chunk the text of the PDFs into smaller pieces with an overlap
    chunk_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = chunk_splitter.split_documents(docs)
    print(f"TOTAL CHUNKS CREATED: {len(chunks)}")

    # clean all chunks up-front and extract document metadata
    cleaned_texts = []
    chunk_metadata = []
    for chunk in chunks:
        cleaned = chunk.page_content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        cleaned_texts.append(" ".join(cleaned.split()))

        source_path = chunk.metadata.get("source", "")
        document_name = os.path.basename(source_path) if source_path else "unknown"
        document_date = datetime.fromtimestamp(os.path.getmtime(source_path)).isoformat() if source_path and os.path.exists(source_path) else "unknown"
        chunk_metadata.append({"document_name": document_name, "document_date": document_date})
    
    print("\n\nCLEANED CHUNK TEXTS:")
    for cleaned_text in cleaned_texts:
        print(f"{repr(cleaned_text)}\n")

    # create embeddings in batches
    BATCH_SIZE = 100
    embeddings_client = createEmbeddingsClient(foundry_url, foundry_key)
    all_embeddings = []
    for i in range(0, len(cleaned_texts), BATCH_SIZE):
        batch = cleaned_texts[i:i + BATCH_SIZE]
        batch_number = i // BATCH_SIZE + 1
        print(f"Embedding batch {batch_number} ({len(batch)} chunks)...")
        all_embeddings.extend(createEmbeddingsBatch(embeddings_client, batch))

    # upload embeddings to Cosmos DB
    cosmos_container = getCosmosContainer(cosmosdb_url, cosmosdb_key, db_name="vectorial_ddbb_poc", container_name="container_for_vectors")
    for i in range(len(cleaned_texts)):
        item = {
            "id": str(i + 1),
            "original_text": cleaned_texts[i],
            "embeddings": all_embeddings[i],
            "document_name": chunk_metadata[i]["document_name"],
            "document_date": chunk_metadata[i]["document_date"]
        }
        uploadToCosmosDB(cosmos_container, item=item)
