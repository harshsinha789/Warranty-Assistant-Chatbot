import os

from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone


# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found")


# Initialize Gemini
gemini_client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": "v1"}
)


# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index("warranty-products")


# User query
query = input("\nEnter your warranty question: ")

# Convert query into an embedding
response = gemini_client.models.embed_content(
    model="gemini-embedding-001",
    contents=query
)

query_embedding = response.embeddings[0].values

# Search Pinecone
results = index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)

print("\nSearch results:\n")

for match in sorted(
    results.matches,
    key=lambda x: x.score,
    reverse=True
):
    print("Score:", match.score)
    print("Product:", match.metadata.get("model"))
    print("Brand:", match.metadata.get("brand"))
    print("Document:", match.metadata.get("document"))

    print("\nWarranty information:")
    print(match.metadata.get("text"))

    print("-" * 70)