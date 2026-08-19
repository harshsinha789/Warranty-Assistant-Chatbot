import os
import sys
import tempfile
import traceback

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

SCRIPTS_DIR = os.path.join(
    PROJECT_ROOT,
    "scripts"
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


# --------------------------------------------------
# Import warranty system
# --------------------------------------------------

from vision_service import analyze_product_image
from warranty_service import (
    assess_warranty,
    get_product
)
from warranty_checker import check_warranty


# --------------------------------------------------
# Warranty API
# --------------------------------------------------

@csrf_exempt
def check_warranty_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only POST requests are allowed."
            },
            status=405
        )


    # --------------------------------------------------
    # Get image
    # --------------------------------------------------

    image = request.FILES.get("image")

    if image is None:

        return JsonResponse(
            {
                "error": "Product image is required."
            },
            status=400
        )


    # --------------------------------------------------
    # Get form data
    # --------------------------------------------------

    purchase_date = request.POST.get(
        "purchase_date",
        ""
    ).strip()

    problem = request.POST.get(
        "problem",
        ""
    ).strip()


    if not purchase_date:

        return JsonResponse(
            {
                "error": "Purchase date is required."
            },
            status=400
        )


    temp_path = None

    try:

        # --------------------------------------------------
        # Save image
        # --------------------------------------------------

        print("\n========== WARRANTY REQUEST ==========")
        print("Saving uploaded image...")

        file_extension = os.path.splitext(
            image.name
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp_file:

            for chunk in image.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        print("Image saved successfully.")


        # --------------------------------------------------
        # Gemini Vision
        # --------------------------------------------------

        print("\n[1/5] Calling Gemini Vision...")

        analysis = analyze_product_image(
            temp_path
        )

        print("Gemini Vision completed.")
        print("Analysis:", analysis)


        # --------------------------------------------------
        # Product identification
        # --------------------------------------------------

        product_id = analysis.get(
            "product_id"
        )

        if product_id == "UNKNOWN":

            return JsonResponse(
                {
                    "status": "NEEDS_VERIFICATION",
                    "message":
                        "I couldn't confidently identify "
                        "the product from the uploaded image."
                }
            )


        print(
            f"Identified product: {product_id}"
        )


        # --------------------------------------------------
        # Get product
        # --------------------------------------------------

        print("\n[2/5] Looking up product...")

        product = get_product(
            product_id
        )

        if product is None:

            return JsonResponse(
                {
                    "status": "NEEDS_VERIFICATION",
                    "message":
                        "The identified product could not "
                        "be found in the warranty database."
                }
            )

        print(
            f"Product found: "
            f"{product['brand']} "
            f"{product['product_name']} "
            f"{product['model']}"
        )


        # --------------------------------------------------
        # Warranty period
        # --------------------------------------------------

        print("\n[3/5] Checking warranty period...")

        try:

            warranty = check_warranty(
                product,
                purchase_date
            )

        except ValueError as e:

            return JsonResponse(
                {
                    "status": "NEEDS_VERIFICATION",
                    "message": str(e)
                },
                status=400
            )

        print(
            "Warranty status:",
            warranty["status"]
        )

        print(
            "Warranty expiry:",
            warranty["expiry_date"]
        )


        # --------------------------------------------------
        # Expired warranty
        # --------------------------------------------------

        if warranty["status"] == "EXPIRED":

            return JsonResponse(
                {
                    "status": "EXPIRED",
                    "message":
                        f"Your warranty expired on "
                        f"{warranty['expiry_date']}.",
                    "product": {
                        "brand": product["brand"],
                        "product": product["product_name"],
                        "model": product["model"]
                    },
                    "purchase_date":
                        warranty["purchase_date"],
                    "expiry_date":
                        warranty["expiry_date"]
                }
            )


        # --------------------------------------------------
        # No problem
        # --------------------------------------------------

        if not problem:

            return JsonResponse(
                {
                    "status": "ACTIVE",
                    "message":
                        f"Your warranty is valid until "
                        f"{warranty['expiry_date']}.",
                    "product": {
                        "brand": product["brand"],
                        "product": product["product_name"],
                        "model": product["model"]
                    },
                    "purchase_date":
                        warranty["purchase_date"],
                    "expiry_date":
                        warranty["expiry_date"]
                }
            )


        # --------------------------------------------------
        # RAG + final assessment
        # --------------------------------------------------

        print("\n[4/5] Starting RAG + warranty assessment...")

        answer = assess_warranty(
            product_id=product_id,
            problem=problem,
            purchase_date=purchase_date,
            damage=analysis
        )

        print("Warranty assessment completed.")


        # --------------------------------------------------
        # Determine status
        # --------------------------------------------------

        if "Not Covered" in answer:

            status = "NOT_COVERED"

        elif "Likely Covered" in answer:

            status = "LIKELY_COVERED"

        elif "Warranty Expired" in answer:

            status = "EXPIRED"

        else:

            status = "NEEDS_VERIFICATION"


        print("\n[5/5] Returning response...")
        print("Status:", status)
        print("======================================\n")


        return JsonResponse(
            {
                "status": status,
                "message": answer,
                "product": {
                    "brand": product["brand"],
                    "product": product["product_name"],
                    "model": product["model"]
                },
                "purchase_date":
                    warranty["purchase_date"],
                "expiry_date":
                    warranty["expiry_date"]
            }
        )


    except Exception as e:

        print("\n!!!!!!!! WARRANTY API ERROR !!!!!!!!")
        print(
            "Error type:",
            type(e).__name__
        )
        print(
            "Error:",
            str(e)
        )

        print("\nFull traceback:")
        traceback.print_exc()

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")


        return JsonResponse(
            {
                "status": "ERROR",
                "message":
                    "Unable to complete the warranty "
                    "assessment.",
                "error_type":
                    type(e).__name__
            },
            status=500
        )


    finally:

        if temp_path and os.path.exists(
            temp_path
        ):

            os.remove(temp_path)