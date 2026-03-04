"""Asks a question and uses RAG with documents previously stored in Cosmos DB to answer it.
1st - embeds the user's question using the same embeddings model used during ingestion
2nd - retrieves the most relevant chunks from Cosmos DB via cosine similarity
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
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utils.math import cosine_similarity
import os

def embedQuery(endpoint, key, text):
    client = AzureOpenAI(
        api_key=key,
        azure_endpoint=endpoint,
        api_version="2023-05-15",
        azure_deployment="text-embedding-3-large",
    )
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def getCosmosContainer(endpoint, key, db_name, container_name):
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(db_name)
    return database.get_container_client(container_name)

def retrieveRelevantChunks(container, query_embedding, top_k=5):
    items = list(container.read_all_items())

    # collect the stored embedding vector from each document
    embeddings = []
    for item in items:
        embeddings.append(item["vectors"])

    # compare the query against all documents at once; one score per document
    scores = cosine_similarity([query_embedding], embeddings)[0]

    # pair each score with its document and sort highest-similarity first
    scored_items = []
    for i, item in enumerate(items):
        scored_items.append((scores[i], item))
    scored_items.sort(key=lambda x: x[0], reverse=True)

    # extract only the original text from the top results
    top_chunks = []
    for _, item in scored_items[:top_k]:
        top_chunks.append(item["original_text"])

    return top_chunks

def requireEnvVar(name):
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"{name} is not set")
    return value

def main():
    foundry_url = requireEnvVar('FOUNDRY_URL')
    foundry_key = requireEnvVar('FOUNDRY_KEY')
    cosmosdb_url = requireEnvVar('COSMOSDB_URL')
    cosmosdb_key = requireEnvVar('COSMOSDB_KEY')

    # TODO: accept the question as user input
    question = "What are profiles for?"

    query_embedding = embedQuery(foundry_url, foundry_key, question)
    cosmos_container = getCosmosContainer(cosmosdb_url, cosmosdb_key, db_name="vectorial_ddbb_poc", container_name="container_for_vectors")
    relevant_chunks = retrieveRelevantChunks(cosmos_container, query_embedding, top_k=5)
    print(f"Retrieved {len(relevant_chunks)} relevant chunks from Cosmos DB\n")

    context = "\n\n".join(relevant_chunks)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer based on the following context. If you don't know something say so. Ask the user for more information if a question isn't clear or is ambiguous. Context:\n\n{context}"),
        ("human", "{question}"),
    ])

    llm = AzureChatOpenAI(
        api_key=foundry_key,
        azure_endpoint=foundry_url,
        api_version="2023-05-15",
        azure_deployment="gpt-4.1",
        temperature=0, # we want the model to stick to facts
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context, "question": question})
    print(response)