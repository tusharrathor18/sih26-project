import re

from scanner.models import ExtractedProductData

FIELD_NAMES = [
    "product_name", "common_or_generic_name", "manufacturer_name", "packer_name",
    "importer_name", "manufacturer_address", "packer_address", "importer_address",
    "country_of_origin", "net_quantity", "quantity_unit", "mrp", "mrp_currency",
    "manufacturing_date", "packing_date", "best_before", "use_by", "consumer_care_name",
    "consumer_care_phone", "consumer_care_email", "unit_sale_price", "dimensions",
    "batch_number", "other_detected_information",
]


def _match(pattern, text, flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else ""


def extract_fields(raw_text, regions=None):
    regions = regions or []
    quantity = re.search(r"(?:net\s*(?:qty|quantity)|quantity)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*(kg|g|mg|l|ml|cl|n)", raw_text, re.I)
    mrp = re.search(r"(?:m\.?r\.?p\.?|maximum\s+retail\s+price)\s*[:\-]?\s*(₹|rs\.?|inr)?\s*([0-9]+(?:[.,][0-9]{1,2})?)", raw_text, re.I)
    email = _match(r"([\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", raw_text, flags=0)
    phone = _match(r"((?:\+?91[\s-]?)?[6-9]\d{9})", raw_text, flags=0)
    country = _match(r"(?:country\s+of\s+origin|made\s+in)\s*[:\-]?\s*([^\n,]+)", raw_text)
    values = {field: "" for field in FIELD_NAMES}
    values.update({
        "net_quantity": quantity.group(1) if quantity else "",
        "quantity_unit": quantity.group(2).lower() if quantity else "",
        "mrp": mrp.group(2) if mrp else "",
        "mrp_currency": mrp.group(1) if mrp and mrp.group(1) else "",
        "country_of_origin": country,
        "consumer_care_email": email,
        "consumer_care_phone": phone,
        "manufacturer_name": _match(r"(?:manufactured|manufactured\s+by)\s*(?:by)?\s*[:\-]?\s*([^\n]+)", raw_text),
        "batch_number": _match(r"(?:batch|lot)\s*(?:no|number)?\s*[:\-]?\s*([^\s\n]+)", raw_text),
        "best_before": _match(r"best\s+before\s*[:\-]?\s*([^\n]+)", raw_text),
    })
    metadata = {
        field: {
            "status": "DETECTED" if value else "NOT_DETECTED",
            "confidence": None,
            "source_regions": [],
        }
        for field, value in values.items()
    }
    if regions:
        for field in ("mrp", "net_quantity", "country_of_origin", "consumer_care_phone", "consumer_care_email"):
            metadata[field]["source_regions"] = regions
    return values, metadata


def save_extraction(inspection, raw_text, regions=None):
    values, metadata = extract_fields(raw_text, regions)
    data, _ = ExtractedProductData.objects.get_or_create(inspection=inspection)
    if not data.original_values:
        data.original_values = values.copy()
    data.values = values
    data.field_metadata = metadata
    data.verification_status = (
        ExtractedProductData.VerificationStatus.DETECTED
        if any(values.values()) else ExtractedProductData.VerificationStatus.NOT_DETECTED
    )
    data.save()
    return data
