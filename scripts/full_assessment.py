from vision_service import analyze_product_image
from warranty_service import assess_warranty
from warranty_checker import check_warranty
from warranty_service import get_product


# --------------------------------------------------
# Get damaged product image
# --------------------------------------------------

image_path = input(
    "Enter your product image path: "
).strip()


# --------------------------------------------------
# Identify product and visible damage
# --------------------------------------------------

print("\nAnalyzing product image...")

try:

    analysis = analyze_product_image(
        image_path
    )

except Exception as e:

    print(
        "\nUnable to analyze the image."
    )

    print(f"Error: {e}")

    exit()


# --------------------------------------------------
# Check product identification
# --------------------------------------------------

if analysis["product_id"] == "UNKNOWN":

    print(
        "\n🟡 Needs Verification\n\n"
        "I couldn't confidently identify the product "
        "from the uploaded image."
    )

    exit()


# --------------------------------------------------
# Display identified product
# --------------------------------------------------

print(
    f"\nProduct identified: "
    f"{analysis['brand']} "
    f"{analysis['model']}"
)

print(
    f"Product confidence: "
    f"{analysis['product_confidence']}"
)


# --------------------------------------------------
# Get product information
# --------------------------------------------------

product = get_product(
    analysis["product_id"]
)

if product is None:

    print(
        "\n🟡 Needs Verification\n\n"
        "The identified product could not be found "
        "in the warranty database."
    )

    exit()


# --------------------------------------------------
# Ask for purchase date IMMEDIATELY
# --------------------------------------------------

purchase_date = input(
    "\nEnter the purchase date (YYYY-MM-DD): "
).strip()


# --------------------------------------------------
# Check warranty period BEFORE further processing
# --------------------------------------------------

try:

    warranty = check_warranty(
        product,
        purchase_date
    )

except ValueError:

    print(
        "\n🟡 Needs Verification\n\n"
        "Invalid purchase date. "
        "Please use YYYY-MM-DD format."
    )

    exit()


# --------------------------------------------------
# Stop immediately if warranty expired
# --------------------------------------------------

if warranty["status"] == "EXPIRED":

    print(
        "\n========================================"
    )

    print(
        "WARRANTY ASSESSMENT"
    )

    print(
        "========================================"
    )

    print(
        "\n🔴 Warranty Expired\n\n"
        f"The warranty expired on "
        f"{warranty['expiry_date']}."
    )

    exit()


# --------------------------------------------------
# Warranty is still valid
# --------------------------------------------------

print(
    "\nWarranty is currently active."
)

print(
    f"Warranty expiry: "
    f"{warranty['expiry_date']}"
)


# --------------------------------------------------
# Ask about the problem
# --------------------------------------------------

problem = input(
    "\nDescribe the problem: "
).strip()


# --------------------------------------------------
# Show damage analysis
# --------------------------------------------------

print(
    "\nVisible damage:"
)

print(
    analysis["damage_description"]
)


# --------------------------------------------------
# Final warranty assessment
# --------------------------------------------------

print(
    "\nAssessing warranty..."
)

try:

    answer = assess_warranty(
        product_id=analysis["product_id"],
        problem=problem,
        purchase_date=purchase_date,
        damage=analysis
    )

except Exception as e:

    print(
        "\nUnable to complete warranty assessment."
    )

    print(f"Error: {e}")

    exit()


# --------------------------------------------------
# Final result
# --------------------------------------------------

print(
    "\n========================================"
)

print(
    "WARRANTY ASSESSMENT"
)

print(
    "========================================"
)

print(answer)