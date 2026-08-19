import os
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found")


# --------------------------------------------------
# Initialize Gemini
# --------------------------------------------------

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": "v1"}
)


# --------------------------------------------------
# Initialize Pinecone
# --------------------------------------------------

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("warranty-products")


# --------------------------------------------------
# Load product database
# --------------------------------------------------

products = pd.read_csv("data/products.csv")


# --------------------------------------------------
# Check warranty period
# --------------------------------------------------

def check_warranty(product_id):

    product = products[
        products["product_id"] == product_id
    ]

    if product.empty:
        return {
            "status": "UNKNOWN",
            "reason": "Product not found."
        }

    product = product.iloc[0]

    purchase_date = date.fromisoformat(
        product["purchase_date"]
    )

    warranty_years = int(
        product["warranty_years"]
    )

    expiry_date = purchase_date + relativedelta(
        years=warranty_years
    )

    today = date.today()

    if today <= expiry_date:

        status = "VALID"

    else:

        status = "EXPIRED"

    return {
        "status": status,
        "product": product["product_name"],
        "brand": product["brand"],
        "model": product["model"],
        "purchase_date": str(purchase_date),
        "expiry_date": str(expiry_date),
        "warranty_years": warranty_years
    }


# --------------------------------------------------
# Retrieve warranty policy
# --------------------------------------------------

def retrieve_policy(query):

    # Convert user query into embedding
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )

    query_embedding = response.embeddings[0].values

    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )

    # Build context
    context_parts = []

    for match in results.matches:

        context_parts.append(
            match.metadata.get("text", "")
        )

    return "\n\n".join(context_parts)


# --------------------------------------------------
# Generate final assessment
# --------------------------------------------------

def generate_assessment(
    product_info,
    warranty_info,
    policy_context,
    user_query
):

    # If product isn't found
    if warranty_info["status"] == "UNKNOWN":

        return "I couldn't identify this product in the warranty database."


    # If warranty has expired
    if warranty_info["status"] == "EXPIRED":

        return (
            "🔴 Warranty Expired\n\n"
            f"The warranty for your {product_info['product_name']} "
            f"expired on {warranty_info['expiry_date']}."
        )


    prompt = f"""
You are a warranty assessment assistant.

Give the user a short and direct answer about whether
their issue appears to be covered by the warranty.

PRODUCT:
Brand: {product_info['brand']}
Product: {product_info['product_name']}
Model: {product_info['model']}

WARRANTY:
Purchase date: {warranty_info['purchase_date']}
Warranty expiry: {warranty_info['expiry_date']}
Warranty status: {warranty_info['status']}

USER'S PROBLEM:
{user_query}

RELEVANT WARRANTY POLICY:
{policy_context}

IMPORTANT RULES:

1. The warranty period is currently VALID.
2. Use ONLY the provided warranty policy.
3. Do not invent warranty conditions.
4. Determine whether the user's specific issue appears
   to be covered or excluded.
5. Give a direct answer.
6. Do not mention Pinecone, embeddings, RAG, databases,
   similarity scores, chunks, or internal processing.
7. Do not list unrelated warranty conditions.
8. Keep the response concise.
9. If the policy does not provide enough information,
   say "Needs Verification".
10. Start the response with exactly one of:

🟢 Likely Covered

🔴 Not Covered

🟡 Needs Verification

Then give a short explanation in 1–2 sentences.
"""

    interaction = gemini_client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text


# --------------------------------------------------
# Main assessment function
# --------------------------------------------------

def assess_warranty(product_id, user_query):

    # Find product
    product = products[
        products["product_id"] == product_id
    ]

    if product.empty:
        return "I couldn't find this product."

    product_info = product.iloc[0].to_dict()

    # Check warranty period
    warranty_info = check_warranty(product_id)

    # If expired, don't waste time on RAG
    if warranty_info["status"] == "EXPIRED":

        return (
            "🔴 Warranty Expired\n\n"
            f"The warranty for your {product_info['product_name']} "
            f"expired on {warranty_info['expiry_date']}."
        )

    # Retrieve relevant warranty information
    policy_context = retrieve_policy(user_query)

    # Generate final answer
    answer = generate_assessment(
        product_info,
        warranty_info,
        policy_context,
        user_query
    )

    return answer


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    product_id = "P005"

    query = (
        "There is a crack on my tv screen "
    "Is it covered?"
    )

    answer = assess_warranty(
        product_id,
        query
    )

    print("\nAssistant:\n")
    print(answer)