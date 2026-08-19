import os
import json
import pandas as pd

from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")


# --------------------------------------------------
# Initialize Gemini
# --------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": "v1"}
)


# --------------------------------------------------
# Load product catalogue
# --------------------------------------------------

products = pd.read_csv("data/products.csv")


# --------------------------------------------------
# Create catalogue for Gemini
# --------------------------------------------------

catalogue = []

for _, product in products.iterrows():

    catalogue.append({
        "product_id": product["product_id"],
        "brand": product["brand"],
        "product_name": product["product_name"],
        "model": product["model"]
    })


catalogue_text = json.dumps(catalogue, indent=2)


# --------------------------------------------------
# Image path
# --------------------------------------------------

image_path = input(
    "Enter the path to the product image: "
).strip()


# --------------------------------------------------
# Upload image
# --------------------------------------------------

image = client.files.upload(
    file=image_path
)


# --------------------------------------------------
# Prompt Gemini
# --------------------------------------------------

prompt = f"""
You are a product identification assistant.

The following is the ONLY product catalogue available:

{catalogue_text}

Analyze the uploaded product image.

Determine which product from the catalogue most likely
matches the image.

IMPORTANT:
- Only select a product from the provided catalogue.
- Do not invent a product.
- Do not invent a model number.
- If the image is insufficient to identify the product,
  return UNKNOWN.
- Return ONLY valid JSON.

Use this exact format:

{{
    "product_id": "P001",
    "brand": "Samsung",
    "product_name": "Washing Machine",
    "model": "WW80T504DAN",
    "confidence": 0.95
}}

If the product cannot be identified:

{{
    "product_id": "UNKNOWN",
    "brand": "",
    "product_name": "",
    "model": "",
    "confidence": 0
}}
"""


# --------------------------------------------------
# Ask Gemini
# --------------------------------------------------

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input=[
        {
            "type": "text",
            "text": prompt
        },
        {
            "type": "image",
            "uri": image.uri,
            "mime_type": image.mime_type
        }
    ]
)


# --------------------------------------------------
# Display result
# --------------------------------------------------

print("\nGemini response:")
print(interaction.output_text)