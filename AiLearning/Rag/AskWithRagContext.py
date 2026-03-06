"""Asks a question and uses RAG with documents previously stored in Cosmos DB to answer it.
1st - embeds the user's question using the same embeddings model used during ingestion
2nd - retrieves the most relevant chunks from Cosmos DB via native vector search (VectorDistance, server-side)
3rd - uses LangChain with the retrieved context to answer the question

Azure resources needed:
    - Azure Foundry with a deployed 'text-embedding-3-large' model
    - Azure Foundry with a deployed chat model (e.g., 'gpt-4o')
    - Cosmos DB instance with documents already uploaded (see CallToInsertChunksIntoCosmos.py)

Config:
    - review the model used to embed the query "text-embedding-3-large" and check it is deployed in your Azure Foundry
    - review the model used to answer questions "gpt-4.1" and check it is deployed in your Foundry
    - set FOUNDRY_URL as system var. This is the URL you get when you deploy models in your Foundry
    - set FOUNDRY_KEY
    - set COSMOSDB_URL
    - set COSMOSDB_KEY

I run this through poetry with 'poetry run x'
"""
import os
import configparser
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

config = configparser.ConfigParser()
config.read("settings.ini")

def embedQuery(endpoint, key, text):
    client = AzureOpenAI(
        api_key=key,
        azure_endpoint=endpoint,
        api_version=config["embedding_model"]["api_version"],
        azure_deployment=config["embedding_model"]["model"],
    )
    response = client.embeddings.create(
        input=[text],
        model=config["embedding_model"]["model"]
    )
    return response.data[0].embedding

def getCosmosContainer(endpoint, key, db_name, container_name):
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(db_name)
    return database.get_container_client(container_name)

def retrieveRelevantChunks(container, query_embedding, top_k=5):
    query = """
        SELECT TOP @top_k c.original_text, VectorDistance(c.embeddings, @embedding) AS score
        FROM c
        ORDER BY VectorDistance(c.embeddings, @embedding)
    """
    parameters = [
        {"name": "@top_k", "value": top_k},
        {"name": "@embedding", "value": query_embedding},
    ]
    results = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    return [r["original_text"] for r in results]

def requireEnvVar(name):
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"{name} is not set")
    return value

def main():
    question = input("Ask a question using RAG: ")
    if not question.strip():
        print("No question provided.")
        return

    foundry_url = requireEnvVar('FOUNDRY_URL')
    foundry_key = requireEnvVar('FOUNDRY_KEY')
    cosmosdb_url = requireEnvVar('COSMOSDB_URL')
    cosmosdb_key = requireEnvVar('COSMOSDB_KEY')

    query_embedding = embedQuery(foundry_url, foundry_key, question)
    cosmos_container = getCosmosContainer(cosmosdb_url, cosmosdb_key, db_name="vectorial_ddbb_poc", container_name="container_for_vectors")
    relevant_chunks = retrieveRelevantChunks(cosmos_container, query_embedding, top_k=5)
    print(f"Retrieved {len(relevant_chunks)} relevant chunks from Cosmos DB\n")

    context = "\n\n".join(relevant_chunks)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer based on the following context and ONLY on the provided context. If you don't have enough context to answer a question please say so. Ask the user for more information if a question isn't clear or is ambiguous. Context:\n\n{context}"),
        ("human", "{question}"),
    ])

    llm = AzureChatOpenAI(
        api_key=foundry_key,
        azure_endpoint=foundry_url,
        api_version=config["chat_model"]["api_version"],
        azure_deployment=config["chat_model"]["model"],
        temperature=0, # we want the model to stick to facts
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context, "question": question})
    clean_response = response.replace("**", "") # remove markdown items as I use this from a console
    print(clean_response)
