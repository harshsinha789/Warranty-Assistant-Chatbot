import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter


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


# Clear existing vectors
print("Clearing existing vectors...")
index.delete(delete_all=True)
print("Existing vectors deleted.")


# Text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


# Find all warranty documents
documents_path = Path("data/warranty_docs")
files = list(documents_path.glob("*.txt"))

print(f"\nFound {len(files)} warranty documents.")


all_vectors = []


# Process every document
for file_path in files:

    print(f"\nProcessing: {file_path.name}")

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Split document into chunks
    chunks = text_splitter.split_text(text)

    print(f"  Chunks created: {len(chunks)}")

    # Extract metadata
    product_id = None
    brand = None
    model = None

    for line in text.splitlines():

        if line.startswith("Product ID:"):
            product_id = line.split(":", 1)[1].strip()

        elif line.startswith("Brand:"):
            brand = line.split(":", 1)[1].strip()

        elif line.startswith("Model:"):
            model = line.split(":", 1)[1].strip()

    # Generate embeddings
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunks
    )

    embeddings = response.embeddings

    # Create Pinecone vectors
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        vector_id = f"{product_id}-chunk-{i}"

        all_vectors.append(
            {
                "id": vector_id,
                "values": embedding.values,
                "metadata": {
                    "product_id": product_id,
                    "brand": brand,
                    "model": model,
                    "document": file_path.name,
                    "chunk_id": i,
                    "text": chunk
                }
            }
        )


# Upload all vectors
print(f"\nUploading {len(all_vectors)} vectors to Pinecone...")

index.upsert(vectors=all_vectors)


print("\n========================================")
print("INGESTION COMPLETED SUCCESSFULLY")
print("========================================")

print(f"Documents processed: {len(files)}")
print(f"Total vectors uploaded: {len(all_vectors)}")