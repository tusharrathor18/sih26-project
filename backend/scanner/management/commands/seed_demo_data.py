from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from compliance.models import Rule
from compliance.services.rule_engine import save_evaluation
from scanner.models import AuditLog, ExtractedProductData, Inspection
from users.models import OfficerProfile


DEMO_INSPECTIONS = (
    {
        "inspection_id": "DEMO-INS-001",
        "username": "inspector_delhi",
        "product_name": "Demo Masala Tea",
        "commodity_category": "TEA",
        "package_type": "RETAIL",
        "consumer_type": "GENERAL",
        "approximate_quantity": Decimal("250"),
        "quantity_unit": "g",
        "values": {
            "product_name": "Demo Masala Tea",
            "common_or_generic_name": "Tea",
            "manufacturer_name": "Demo Foods Pvt Ltd, Demo Industrial Area",
            "packer_name": "Demo Foods Pvt Ltd",
            "importer_name": "",
            "manufacturer_address": "Demo Industrial Area",
            "packer_address": "Demo Industrial Area",
            "importer_address": "",
            "country_of_origin": "India",
            "net_quantity": "250",
            "quantity_unit": "g",
            "mrp": "120",
            "mrp_currency": "INR",
            "manufacturing_date": "01/2026",
            "packing_date": "",
            "best_before": "12 months",
            "use_by": "",
            "consumer_care_name": "Demo Consumer Care",
            "consumer_care_phone": "1800000000",
            "consumer_care_email": "care@example.invalid",
            "unit_sale_price": "0.48/g",
            "dimensions": "",
            "batch_number": "DEMO001",
            "other_detected_information": "DEMO DATA - not a real inspection",
        },
    },
    {
        "inspection_id": "DEMO-INS-002",
        "username": "inspector_delhi",
        "product_name": "Demo Missing Declaration Pack",
        "commodity_category": "BISCUITS",
        "package_type": "RETAIL",
        "consumer_type": "GENERAL",
        "approximate_quantity": Decimal("100"),
        "quantity_unit": "g",
        "values": {
            "product_name": "Demo Missing Declaration Pack",
            "common_or_generic_name": "",
            "manufacturer_name": "",
            "packer_name": "",
            "importer_name": "",
            "manufacturer_address": "",
            "packer_address": "",
            "importer_address": "",
            "country_of_origin": "India",
            "net_quantity": "100",
            "quantity_unit": "g",
            "mrp": "50",
            "mrp_currency": "INR",
            "manufacturing_date": "",
            "packing_date": "",
            "best_before": "",
            "use_by": "",
            "consumer_care_name": "",
            "consumer_care_phone": "",
            "consumer_care_email": "",
            "unit_sale_price": "",
            "dimensions": "",
            "batch_number": "DEMO002",
            "other_detected_information": "DEMO DATA - not a real inspection",
        },
    },
)


class Command(BaseCommand):
    help = "Create reproducible, clearly marked local demo data after migrations."

    @transaction.atomic
    def handle(self, *args, **options):
        call_command("seed_officers", verbosity=0)
        if not Rule.objects.exists():
            call_command("seed_rules", verbosity=0)

        for definition in DEMO_INSPECTIONS:
            officer = OfficerProfile.objects.get(user__username=definition["username"]).user
            inspection, created = Inspection.objects.get_or_create(
                inspection_id=definition["inspection_id"],
                defaults={
                    "officer": officer,
                    "product_name": definition["product_name"],
                    "commodity_category": definition["commodity_category"],
                    "package_type": definition["package_type"],
                    "consumer_type": definition["consumer_type"],
                    "approximate_quantity": definition["approximate_quantity"],
                    "quantity_unit": definition["quantity_unit"],
                    "status": Inspection.Status.READY_FOR_COMPLIANCE,
                    "verified_by": officer,
                    "verified_at": timezone.now(),
                },
            )
            if not created:
                self.stdout.write(f"Demo inspection {inspection.inspection_id} already exists; unchanged.")
                continue

            extracted, _ = ExtractedProductData.objects.get_or_create(
                inspection=inspection,
                defaults={
                    "values": definition["values"],
                    "original_values": definition["values"],
                    "field_metadata": {
                        field: {"status": "DETECTED" if value else "NOT_DETECTED", "confidence": 0.99 if value else None, "source_regions": []}
                        for field, value in definition["values"].items()
                    },
                    "verification_status": ExtractedProductData.VerificationStatus.VERIFIED,
                    "verified_by": officer,
                    "verified_at": timezone.now(),
                },
            )
            evaluation, _ = save_evaluation(inspection)
            inspection.status = Inspection.Status.READY_FOR_COMPLIANCE
            inspection.save(update_fields=["status", "updated_at"])
            for action, description in (
                ("INSPECTION_CREATED", "Demo inspection created. DEMO DATA - not a real inspection."),
                ("OCR_COMPLETED", "Demo extracted information prepared without running OCR."),
                ("INSPECTION_VERIFIED", "Demo information marked as officer-verified for local demonstration."),
                ("COMPLIANCE_RUN", f"Demo compliance evaluation completed, version {evaluation.evaluation_version}."),
            ):
                AuditLog.objects.get_or_create(
                    inspection=inspection,
                    action=action,
                    defaults={"user": officer, "description": description, "metadata": {"demo": True}},
                )
            self.stdout.write(self.style.SUCCESS(f"Created demo inspection {inspection.inspection_id}."))

        self.stdout.write(self.style.SUCCESS("Demo data initialization complete."))
