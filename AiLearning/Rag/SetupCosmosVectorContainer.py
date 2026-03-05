"""Recreates the Cosmos DB container with vector search policies enabled.
This deletes the existing container (and all its data) and creates a new one
configured for native vector search with the VectorDistance system function.

Run this ONCE before ingesting data with ChunkFilesIntoCosmos.py.
After running this, re-ingest your documents so they are stored in the vector-enabled container.

Config:
    - set COSMOSDB_URL as system var
    - set COSMOSDB_KEY as system var
    - review db_name and container_name below to match your setup
    - review dimensions (3072 for text-embedding-3-large)
    - review vector index type: "quantizedFlat" for small datasets, "diskANN" for large datasets

I run this through poetry with 'poetry run x'
"""
from azure.cosmos import CosmosClient, PartitionKey
import os

DB_NAME = "vectorial_ddbb_poc"
CONTAINER_NAME = "container_for_vectors"

def requireEnvVar(name):
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"{name} is not set")
    return value

def main():
    cosmosdb_url = requireEnvVar('COSMOSDB_URL')
    cosmosdb_key = requireEnvVar('COSMOSDB_KEY')

    client = CosmosClient(cosmosdb_url, cosmosdb_key)
    database = client.get_database_client(DB_NAME)

    # delete old container if it exists (this removes all data)
    try:
        database.delete_container(CONTAINER_NAME)
        print(f"Deleted existing container '{CONTAINER_NAME}'")
    except Exception:
        print(f"No existing container '{CONTAINER_NAME}' found, creating fresh")

    # defines which fields hold vectors, their dimensions, data type, and distance function
    vector_embedding_policy = {
        "vectorEmbeddings": [
            {
                "path": "/embeddings",
                "dataType": "float32",
                "distanceFunction": "cosine",
                "dimensions": 3072  # text-embedding-3-large outputs 3072 dimensions
            }
        ]
    }

    # tells Cosmos DB to build a vector index on the /embeddings path
    # "quantizedFlat" works for small datasets (< ~10k items), switch to "diskANN" for larger ones
    indexing_policy = {
        "includedPaths": [
            {"path": "/*"}
        ],
        "excludedPaths": [
            {"path": "/embeddings/*"}  # exclude vector data from the regular (BTree) index
        ],
        "vectorIndexes": [
            {"path": "/embeddings", "type": "quantizedFlat"}
        ]
    }

    container = database.create_container(
        id=CONTAINER_NAME,
        partition_key=PartitionKey(path="/id"),
        indexing_policy=indexing_policy,
        vector_embedding_policy=vector_embedding_policy,
    )

    print(f"Created container '{CONTAINER_NAME}' with vector search enabled")
    print(f"  - Vector path:      /embeddings")
    print(f"  - Dimensions:       3072")
    print(f"  - Distance function: cosine")
    print(f"  - Index type:       quantizedFlat")
    print(f"\nNext step: run the script to re-ingest your documents.")