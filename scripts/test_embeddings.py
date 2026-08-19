import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1"}
)

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Charging circuit failure is covered under the warranty."
)

embedding = response.embeddings[0].values

print("Embedding generated successfully!")
print("Embedding dimension:", len(embedding))
print("First 5 values:", embedding[:5])