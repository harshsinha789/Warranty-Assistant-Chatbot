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


# User question
query = "My Dell laptop is not charging. Is this covered under warranty?"


# --------------------------------------------------
# 1. Convert question into an embedding
# --------------------------------------------------

response = gemini_client.models.embed_content(
    model="gemini-embedding-001",
    contents=query
)

query_embedding = response.embeddings[0].values


# --------------------------------------------------
# 2. Retrieve relevant warranty information
# --------------------------------------------------

results = index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)


# --------------------------------------------------
# 3. Build context from retrieved documents
# --------------------------------------------------

context = ""

for match in results.matches:

    context += match.metadata.get("text", "")
    context += "\n\n"


# --------------------------------------------------
# 4. Create prompt for Gemini
# --------------------------------------------------

prompt = f"""
You are a warranty assistance chatbot.

Answer the user's question using ONLY the warranty
information provided in the context below.

Do not invent warranty conditions.

If the information is insufficient to determine
whether the issue is covered, clearly say that
additional information is required.

Warranty context:
------------------
{context}
------------------

User question:
{query}

Give a concise answer and explain the reason.
"""


# --------------------------------------------------
# 5. Generate answer
# --------------------------------------------------

interaction = gemini_client.interactions.create(
    model="gemini-3.6-flash",
    input=prompt
)


# --------------------------------------------------
# 6. Display answer
# --------------------------------------------------

print("\nUser:")
print(query)

print("\nAssistant:")
print(interaction.output_text)