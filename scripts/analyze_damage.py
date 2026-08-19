import os
import json

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
# Get image path
# --------------------------------------------------

image_path = input(
    "Enter the path to the damage/problem image: "
).strip()


# --------------------------------------------------
# Upload image
# --------------------------------------------------

image = client.files.upload(
    file=image_path
)


# --------------------------------------------------
# Prompt
# --------------------------------------------------

prompt = """
You are a product damage assessment assistant.

Analyze the uploaded product image.

Identify ONLY visible physical damage or visible signs
of a product problem.

Do NOT assume an internal hardware failure if it cannot
be seen in the image.

Examples of visible damage:
- Cracked screen
- Broken component
- Dent
- Scratch
- Burn marks
- Cracked casing
- Broken lens
- Physical impact damage
- Liquid/water damage if visibly apparent

If there is no obvious visible damage, report that.

Return ONLY valid JSON using this format:

{
    "visible_damage": true,
    "damage_type": "physical_damage",
    "description": "Brief description of what is visibly damaged.",
    "confidence": 0.95
}

If no visible damage is present:

{
    "visible_damage": false,
    "damage_type": "none",
    "description": "No obvious physical damage is visible.",
    "confidence": 0.90
}
"""


# --------------------------------------------------
# Analyze image
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