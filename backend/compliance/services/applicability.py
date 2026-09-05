from decimal import Decimal


def _quantity_in_base(inspection):
    if inspection.approximate_quantity is None:
        return None
    unit = (inspection.quantity_unit or "").lower()
    multiplier = {"kg": Decimal("1000"), "g": Decimal("1"), "mg": Decimal("0.001"), "l": Decimal("1000"), "ml": Decimal("1")}.get(unit)
    return inspection.approximate_quantity * multiplier if multiplier else None


def determine_applicability(inspection):
    reasons = []
    quantity = _quantity_in_base(inspection)
    consumer = (inspection.consumer_type or "").upper()
    category = (inspection.commodity_category or "").upper()
    if consumer in {"INDUSTRIAL", "INSTITUTIONAL"}:
        reasons.append(f"Chapter II exclusion: {consumer.lower()} consumer.")
    if quantity is not None and quantity > Decimal("25000") and category not in {"CEMENT", "FERTILIZER"}:
        reasons.append("Chapter II exclusion: package exceeds 25 kg/25 litres.")
    if quantity is not None and quantity <= Decimal("10"):
        reasons.append("Rule 26 small-package exemption: quantity is 10 g/ml or less.")
    if inspection.package_type.upper() == "WHOLESALE":
        return {"status": "APPLICABLE", "chapter_ii": True, "reasons": reasons, "exemptions": [], "package_type": "WHOLESALE"}
    if consumer in {"INDUSTRIAL", "INSTITUTIONAL"}:
        return {"status": "NOT_APPLICABLE", "chapter_ii": False, "reasons": reasons, "exemptions": reasons, "package_type": inspection.package_type}
    if quantity is None and not consumer and not inspection.package_type:
        return {"status": "MANUAL_REVIEW", "chapter_ii": None, "reasons": ["Package quantity, consumer type and package type are not sufficiently identified."], "exemptions": [], "package_type": ""}
    if quantity is not None and quantity <= Decimal("10"):
        return {"status": "NOT_APPLICABLE", "chapter_ii": False, "reasons": reasons, "exemptions": reasons, "package_type": inspection.package_type}
    return {"status": "APPLICABLE", "chapter_ii": True, "reasons": reasons, "exemptions": [], "package_type": inspection.package_type}
