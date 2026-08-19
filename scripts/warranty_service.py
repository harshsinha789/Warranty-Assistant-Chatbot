import os
import json
import pandas as pd

from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone

from warranty_checker import check_warranty


# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(
    os.path.join(
        PROJECT_ROOT,
        ".env"
    )
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

if not PINECONE_API_KEY:
    raise ValueError(
        "PINECONE_API_KEY not found in .env"
    )


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

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    "warranty-products"
)


# --------------------------------------------------
# Load product catalogue
# --------------------------------------------------

products = pd.read_csv(
    os.path.join(
        PROJECT_ROOT,
        "data",
        "products.csv"
    )
)


# --------------------------------------------------
# Get product information
# --------------------------------------------------

def get_product(product_id):

    product = products[
        products["product_id"] == product_id
    ]

    if product.empty:
        return None

    return product.iloc[0].to_dict()


# --------------------------------------------------
# Retrieve relevant warranty policy from Pinecone
# --------------------------------------------------

def retrieve_policy(
    query,
    product_id
):

    # Generate embedding for the user's problem
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )

    query_embedding = (
        response.embeddings[0].values
    )

    # Search only the identified product's
    # warranty documents
    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True,
        filter={
            "product_id": product_id
        }
    )

    # Collect relevant policy text
    context_parts = []

    for match in results.matches:

        text = match.metadata.get(
            "text",
            ""
        )

        if text:
            context_parts.append(text)

    return "\n\n".join(
        context_parts
    )


# --------------------------------------------------
# Generate final user-facing answer
# --------------------------------------------------

def generate_final_answer(
    product,
    warranty,
    policy,
    problem,
    damage
):

    prompt = f"""
You are a concise warranty assessment assistant.

PRODUCT:
Brand: {product["brand"]}
Product: {product["product_name"]}
Model: {product["model"]}

WARRANTY:
Status: {warranty["status"]}
Purchase date: {warranty["purchase_date"]}
Warranty expiry: {warranty["expiry_date"]}
Warranty duration: {warranty["warranty_years"]} years

USER'S PROBLEM:
{problem}

VISIBLE DAMAGE ANALYSIS:
{json.dumps(damage, indent=2)}

RELEVANT WARRANTY POLICY:
{policy}

RULES:

1. Give the user a direct warranty assessment.

2. Start with exactly ONE of these:

🟢 Likely Covered

🔴 Not Covered

🟡 Needs Verification

3. Use ONLY the supplied warranty policy.

4. Do not invent warranty conditions.

5. The warranty period has already been checked
   by the application.

6. If the warranty status is EXPIRED, clearly state
   that the warranty has expired.

7. If visible physical or accidental damage is present,
   consider the relevant exclusions in the warranty policy.

8. Do not claim that an image proves an internal
   manufacturing defect.

9. Consider the user's description together with
   the visible damage.

10. If the available information is insufficient to
    determine coverage, use "Needs Verification".

11. Keep the explanation to 1–2 short sentences.

12. Do not mention:
    - Pinecone
    - RAG
    - embeddings
    - databases
    - retrieved chunks
    - similarity scores
    - prompts
    - internal processing

13. Do not list unrelated warranty conditions.

Return ONLY the concise user-facing assessment.
"""

    # Use the faster model for the final response
    interaction = gemini_client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    return interaction.output_text.strip()


# --------------------------------------------------
# Main warranty assessment
# --------------------------------------------------

def assess_warranty(
    product_id,
    problem,
    purchase_date,
    damage
):

    # ----------------------------------------------
    # Find product
    # ----------------------------------------------

    product = get_product(
        product_id
    )

    if product is None:

        return (
            "🟡 Needs Verification\n\n"
            "I couldn't identify this product "
            "in the warranty database."
        )


    # ----------------------------------------------
    # Check warranty period
    # ----------------------------------------------

    try:

        warranty = check_warranty(
            product,
            purchase_date
        )

    except ValueError:

        return (
            "🟡 Needs Verification\n\n"
            "The purchase date provided is invalid. "
            "Please enter the date in YYYY-MM-DD format."
        )


    # ----------------------------------------------
    # If warranty has expired
    # ----------------------------------------------

    if warranty["status"] == "EXPIRED":

        return (
            "🔴 Warranty Expired\n\n"
            f"The warranty expired on "
            f"{warranty['expiry_date']}."
        )


    # ----------------------------------------------
    # Build RAG query
    # ----------------------------------------------

    retrieval_query = f"""
Product:
{product["brand"]} {product["product_name"]}

Model:
{product["model"]}

User problem:
{problem}

Visible damage:
{damage.get("damage_description", "")}

Damage type:
{damage.get("damage_type", "none")}
"""


    # ----------------------------------------------
    # Retrieve product-specific policy
    # ----------------------------------------------

    policy = retrieve_policy(
        retrieval_query,
        product_id
    )


    # ----------------------------------------------
    # Generate final assessment
    # ----------------------------------------------

    answer = generate_final_answer(
        product,
        warranty,
        policy,
        problem,
        damage
    )

    return answer