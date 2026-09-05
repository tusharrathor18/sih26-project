from decimal import Decimal, InvalidOperation

from django.utils import timezone

from compliance.models import ComplianceEvaluation, ComplianceResult, Rule, ScheduleEntry, StandardPackSize
from .applicability import determine_applicability


FIELD_RULES = {
    "manufacturer_name": "Manufacturer / packer / importer identity and address",
    "common_or_generic_name": "Common or generic name",
    "net_quantity": "Net quantity",
    "manufacturing_date": "Month and year of manufacture, pre-packing or import",
    "mrp": "Retail sale price",
    "consumer_care_phone": "Consumer complaint contact information",
}


def _number(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError, ValueError):
        return None


def _result(rule, status, detected="", expected="", explanation="", recommendation="", evidence=None, source_field=""):
    return {"rule": rule, "status": status, "detected_value": detected or "", "expected_requirement": expected or rule.requirement, "explanation": explanation, "recommendation": recommendation, "evidence": evidence or {}, "source_ocr_field": source_field, "severity": rule.severity}


def _field_result(rule, values, metadata, field, label):
    value = values.get(field, "")
    field_meta = metadata.get(field, {})
    confidence = field_meta.get("confidence")
    evidence = {"ocr_field": field, "confidence": confidence, "source_regions": field_meta.get("source_regions", [])}
    if not value:
        return _result(rule, "MANUAL_REVIEW", "Not detected", label, f"{label} could not be reliably detected from the supplied images.", "Verify the package manually.", evidence, field)
    if confidence is not None and confidence < 0.60:
        return _result(rule, "MANUAL_REVIEW", value, label, "The detected value has low OCR confidence.", "Verify the declaration manually.", evidence, field)
    return _result(rule, "PASS", value, label, f"{label} was detected in the verified extracted data.", "", evidence, field)


def _standard_pack_result(rule, inspection, values):
    category = inspection.commodity_category.upper()
    pack_category = next((c for c in StandardPackSize.objects.values_list("category__code", flat=True) if c == category), None)
    declared = _number(values.get("net_quantity"))
    unit = (values.get("quantity_unit") or inspection.quantity_unit or "").lower()
    if not pack_category or declared is None or not unit:
        return _result(rule, "MANUAL_REVIEW", values.get("net_quantity", "Not detected"), "Second Schedule standard pack size", "Commodity category or normalized quantity is missing.", "Confirm commodity category and package quantity.")
    sizes = StandardPackSize.objects.filter(category__code=pack_category)
    converted = declared * (Decimal("1000") if unit in {"kg", "l"} else Decimal("1"))
    matches = any((size.quantity_value * (Decimal("1000") if size.quantity_unit in {"kg", "l"} else Decimal("1"))) == converted for size in sizes)
    return _result(rule, "PASS" if matches else "MANUAL_REVIEW", f"{declared} {unit}", "A quantity listed in the Second Schedule", "Declared size matches a seeded standard size." if matches else "The PDF schedule includes continuation/multiple conditions that require category-specific verification.", "", {"schedule": "Second Schedule", "source_page": 29})


def _mpe_result(rule, inspection, values):
    declared = _number(values.get("net_quantity"))
    actual = inspection.actual_measured_quantity
    if declared is None or actual is None:
        return _result(rule, "MANUAL_REVIEW", values.get("net_quantity", "Not detected"), "First Schedule maximum permissible error", "Actual physical measurement is not available; OCR cannot establish quantity accuracy.", "Enter an authorised physical measurement before evaluating MPE.")
    deficiency = declared - actual
    unit = (values.get("quantity_unit") or inspection.measurement_unit or "").lower()
    base = declared * (Decimal("1000") if unit in {"kg", "l"} else Decimal("1"))
    rows = ScheduleEntry.objects.filter(schedule="FIRST", source_reference="First Schedule").exclude(commodity__in=["Length", "Area", "Number"])
    selected = next((row for row in rows if row.data.get("max") is None or base <= Decimal(str(row.data["max"]))), None)
    if selected is None:
        return _result(rule, "MANUAL_REVIEW", str(actual), "First Schedule MPE", "No applicable First Schedule band could be selected.", "Confirm the unit and declared quantity.")
    mpe = Decimal(str(selected.data["mpe"]))
    allowed = mpe if selected.data["kind"] == "absolute" else base * mpe / Decimal("100")
    status = "PASS" if deficiency <= allowed else "FAIL"
    return _result(rule, status, f"declared={declared}, actual={actual}, deficiency={deficiency}", str(allowed), f"First Schedule MPE applied using {selected.commodity}.", "Record the physical measurement and investigate a failed MPE result." if status == "FAIL" else "", {"declared": str(declared), "actual": str(actual), "deficiency": str(deficiency), "mpe": str(allowed), "source_page": 28})


def evaluate_inspection(inspection):
    applicability = determine_applicability(inspection)
    extracted = getattr(inspection, "extracted_data", None)
    values = extracted.values if extracted else {}
    metadata = extracted.field_metadata if extracted else {}
    rules = list(Rule.objects.filter(is_active=True))
    outputs = []
    for rule in rules:
        if applicability["status"] == "NOT_APPLICABLE" and rule.rule_number not in {"3", "26"}:
            outputs.append(_result(rule, "NOT_APPLICABLE", "", "Chapter II applicability", "Chapter II does not apply under the recorded applicability facts.", "No Chapter II declaration result is issued."))
            continue
        if rule.rule_number == "3":
            status = "PASS" if applicability["status"] == "APPLICABLE" else applicability["status"]
            outputs.append(_result(rule, status, "; ".join(applicability["reasons"]), "Chapter II applicability determined before validation", "Applicability was evaluated from package facts.", "Complete package quantity, type and consumer details." if status == "MANUAL_REVIEW" else ""))
        elif rule.rule_number == "5":
            outputs.append(_standard_pack_result(rule, inspection, values))
        elif rule.rule_number == "6":
            results = [_field_result(rule, values, metadata, field, label) for field, label in FIELD_RULES.items()]
            outputs.append(_result(rule, "PASS" if all(item["status"] == "PASS" for item in results) else "MANUAL_REVIEW", "; ".join(item["detected_value"] for item in results), "All applicable Rule 6 declarations", "Individual declaration checks are preserved in evidence.", "Verify missing or low-confidence declarations.", {"declarations": results}))
        elif rule.rule_number == "10":
            outputs.append(_field_result(rule, values, metadata, "manufacturer_name", "Manufacturer/packer/importer information"))
        elif rule.rule_number == "11":
            outputs.append(_field_result(rule, values, metadata, "net_quantity", "Net quantity excluding packaging"))
        elif rule.rule_number in {"12", "13"}:
            outputs.append(_field_result(rule, values, metadata, "quantity_unit", "Applicable quantity unit"))
        elif rule.rule_number == "16":
            outputs.append(_result(rule, "NOT_APPLICABLE" if inspection.commodity_category.upper() != "SHEET_COMMODITY" else "MANUAL_REVIEW", "", "Usable sheet count and dimensions", "Sheet declaration requires applicable product identification.", "Verify sheet count and dimensions manually."))
        elif rule.rule_number == "17":
            outputs.append(_result(rule, "NOT_APPLICABLE" if inspection.commodity_category.upper() != "CONTAINER_COMMODITY" else "MANUAL_REVIEW", "", "Container dimensions/capacity/number", "Container commodity was not identified." if inspection.commodity_category.upper() != "CONTAINER_COMMODITY" else "Container details cannot be fully established from OCR alone.", ""))
        elif rule.rule_number == "22":
            outputs.append(_mpe_result(rule, inspection, values))
        elif rule.rule_number == "26":
            outputs.append(_result(rule, "NOT_APPLICABLE" if applicability["status"] != "NOT_APPLICABLE" else "PASS", "; ".join(applicability["reasons"]), "Rule 26 exemptions", "Exemption status was evaluated before rule checks.", ""))
        elif rule.rule_number == "24":
            outputs.append(_result(rule, "MANUAL_REVIEW" if inspection.package_type.upper() == "WHOLESALE" else "NOT_APPLICABLE", "", "Wholesale declarations", "Wholesale status requires inspection facts and package evidence." if inspection.package_type.upper() == "WHOLESALE" else "Package is not identified as wholesale.", ""))
        elif rule.rule_number == "31":
            outputs.append(_result(rule, "MANUAL_REVIEW" if inspection.package_type.upper() == "ADVERTISEMENT" else "NOT_APPLICABLE", "", "Advertisement retail-price and quantity declarations", "Advertisement status requires inspection classification." if inspection.package_type.upper() == "ADVERTISEMENT" else "Inspection is not identified as an advertisement.", ""))
        else:
            outputs.append(_result(rule, "MANUAL_REVIEW", "", rule.requirement, "This provision cannot be reliably established from the available structured extraction alone.", "Authorised officer/legal verification required."))
    return applicability, outputs


def save_evaluation(inspection):
    applicability, outputs = evaluate_inspection(inspection)
    current = ComplianceEvaluation.objects.filter(inspection=inspection, is_current=True).first()
    next_version = (current.evaluation_version + 1) if current else 1
    if current:
        current.is_current = False
        current.superseded_at = timezone.now()
        current.save(update_fields=["is_current", "superseded_at"])
    evaluation = ComplianceEvaluation.objects.create(
        inspection=inspection,
        evaluation_version=next_version,
        is_current=True,
        overall_status="INCONCLUSIVE",
    )
    ComplianceResult.objects.bulk_create([ComplianceResult(evaluation=evaluation, **output) for output in outputs])
    counts = {status: sum(1 for output in outputs if output["status"] == status) for status in ComplianceResult.Status.values}
    if counts["FAIL"]:
        overall = ComplianceEvaluation.OverallStatus.NON_COMPLIANT
    elif counts["MANUAL_REVIEW"] or counts["WARNING"]:
        overall = ComplianceEvaluation.OverallStatus.NEEDS_MANUAL_REVIEW
    elif outputs and counts["PASS"] == len(outputs):
        overall = ComplianceEvaluation.OverallStatus.COMPLIANT
    else:
        overall = ComplianceEvaluation.OverallStatus.INCONCLUSIVE
    evaluation.overall_status = overall
    evaluation.total_rules = len(outputs)
    evaluation.passed = counts["PASS"]
    evaluation.failed = counts["FAIL"]
    evaluation.warnings = counts["WARNING"]
    evaluation.manual_review = counts["MANUAL_REVIEW"]
    evaluation.not_applicable = counts["NOT_APPLICABLE"]
    evaluation.save()
    return evaluation, applicability
