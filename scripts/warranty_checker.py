from datetime import date
from dateutil.relativedelta import relativedelta


def check_warranty(product, purchase_date):
    """
    Check whether a product is still within its warranty period.

    Parameters:
        product: Dictionary containing product information,
                 including warranty_years.
        purchase_date: Purchase date in YYYY-MM-DD format.

    Returns:
        Dictionary containing warranty status,
        purchase date, expiry date, and warranty duration.

    Raises:
        ValueError: If the purchase date is invalid or is in the future.
    """

    # --------------------------------------------------
    # Convert user-provided string to a date object
    # --------------------------------------------------

    try:
        purchase_date = date.fromisoformat(
            purchase_date
        )

    except ValueError:
        raise ValueError(
            "Invalid purchase date. "
            "Please use YYYY-MM-DD format."
        )


    # --------------------------------------------------
    # Prevent future purchase dates
    # --------------------------------------------------

    today = date.today()

    if purchase_date > today:

        raise ValueError(
            "Purchase date cannot be in the future."
        )


    # --------------------------------------------------
    # Get warranty duration from product catalogue
    # --------------------------------------------------

    warranty_years = int(
        product["warranty_years"]
    )


    # --------------------------------------------------
    # Calculate warranty expiry date
    # --------------------------------------------------

    expiry_date = purchase_date + relativedelta(
        years=warranty_years
    )


    # --------------------------------------------------
    # Determine warranty status
    # --------------------------------------------------

    if today <= expiry_date:

        status = "VALID"

    else:

        status = "EXPIRED"


    # --------------------------------------------------
    # Return warranty information
    # --------------------------------------------------

    return {
        "status": status,
        "purchase_date": str(purchase_date),
        "expiry_date": str(expiry_date),
        "warranty_years": warranty_years
    }