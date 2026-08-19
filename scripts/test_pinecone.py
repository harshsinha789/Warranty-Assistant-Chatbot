import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise ValueError("PINECONE_API_KEY not found")

pc = Pinecone(api_key=api_key)

print("Available indexes:")

for index in pc.list_indexes():
    print("-", index.name)

print("\nPinecone connection successful!")