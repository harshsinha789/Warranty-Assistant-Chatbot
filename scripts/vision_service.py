import os
import json
import base64
import pandas as pd

from dotenv import load_dotenv
from google import genai


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

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# --------------------------------------------------
# Initialize Gemini
# --------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={
        "api_version": "v1"
    }
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
# Extract JSON from Gemini response
# --------------------------------------------------

def extract_json(text):

    text = text.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        # Remove ```json
        lines = lines[1:]

        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)


# --------------------------------------------------
# Analyze product image
# --------------------------------------------------

def analyze_product_image(image_path):

    # --------------------------------------------------
    # Build product catalogue
    # --------------------------------------------------

    catalogue = []

    for _, product in products.iterrows():

        catalogue.append({
            "product_id": product["product_id"],
            "brand": product["brand"],
            "product_name": product["product_name"],
            "model": product["model"]
        })

    catalogue_text = json.dumps(
        catalogue,
        indent=2
    )


    # --------------------------------------------------
    # Read image
    # --------------------------------------------------

    with open(
        image_path,
        "rb"
    ) as f:

        image_bytes = f.read()


    image_data = base64.b64encode(
        image_bytes
    ).decode("utf-8")


    # --------------------------------------------------
    # Determine image MIME type
    # --------------------------------------------------

    extension = os.path.splitext(
        image_path
    )[1].lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }

    mime_type = mime_types.get(
        extension,
        "image/jpeg"
    )


    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    prompt = f"""
You are a multimodal warranty inspection assistant.

The user has uploaded ONE image of a potentially
damaged or faulty product.

Your task is to perform TWO things:

1. Identify the product from the provided catalogue.
2. Analyze any visible physical damage.

AVAILABLE PRODUCT CATALOGUE:

{catalogue_text}

PRODUCT IDENTIFICATION RULES:

- Select ONLY a product from the catalogue.
- Do not invent a product.
- Do not invent a model number.
- Use visible brand, design, model markings, and
  other visual clues.
- If the product cannot be identified confidently,
  return UNKNOWN.

DAMAGE ANALYSIS RULES:

- Report only damage that is actually visible.
- Do not claim that an internal component has failed
  merely because the product is not working.
- A photograph cannot prove that a defect is a
  manufacturing defect.
- If there is no obvious physical damage,
  report none.
- Examples include cracked screens, dents,
  broken components, scratches, burn marks,
  cracked casing, broken lenses, and visible
  liquid damage.

Return ONLY valid JSON using exactly this structure:

{{
    "product_id": "P001",
    "brand": "Samsung",
    "product_name": "Washing Machine",
    "model": "WW80T504DAN",
    "product_confidence": 0.95,

    "visible_damage": true,
    "damage_type": "physical_damage",
    "damage_description": "The product has visible physical damage.",
    "damage_confidence": 0.95
}}

If the product cannot be identified:

{{
    "product_id": "UNKNOWN",
    "brand": "",
    "product_name": "",
    "model": "",
    "product_confidence": 0,

    "visible_damage": true,
    "damage_type": "physical_damage",
    "damage_description": "Description of visible damage.",
    "damage_confidence": 0.90
}}

If no physical damage is visible:

{{
    "product_id": "P001",
    "brand": "Samsung",
    "product_name": "Washing Machine",
    "model": "WW80T504DAN",
    "product_confidence": 0.95,

    "visible_damage": false,
    "damage_type": "none",
    "damage_description": "No obvious physical damage is visible.",
    "damage_confidence": 0.90
}}
"""


    # --------------------------------------------------
    # Gemini Vision
    # --------------------------------------------------

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=[
            {
                "type": "image",
                "data": image_data,
                "mime_type": mime_type
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    )


    # --------------------------------------------------
    # Parse Gemini response
    # --------------------------------------------------

    return extract_json(
        interaction.output_text
    )