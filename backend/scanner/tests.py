from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from users.models import OfficerProfile

from .models import Inspection, InspectionImage
from .services.extraction_service import extract_fields
from .services.image_processing import process_image


def image_file(name="label.png"):
    buffer = BytesIO()
    Image.new("RGB", (1200, 900), "white").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class InspectionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="scanner_one", password="TestPassword@123")
        OfficerProfile.objects.create(
            user=self.user,
            officer_id="OFF-SCAN-001",
            name="Scanner Inspector",
            designation="Inspector",
            jurisdiction="Zone 1",
            role="INSPECTOR",
        )
        self.other_user = User.objects.create_user(username="scanner_two", password="TestPassword@123")
        OfficerProfile.objects.create(
            user=self.other_user,
            officer_id="OFF-SCAN-002",
            name="Other Inspector",
            designation="Inspector",
            jurisdiction="Zone 2",
            role="INSPECTOR",
        )
        self.client.force_authenticate(self.user)

    def test_unauthenticated_cannot_create_inspection(self):
        self.client.force_authenticate(None)
        response = self.client.post("/api/scanner/inspections/", {}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_multiple_images_and_owner_isolation(self):
        created = self.client.post("/api/scanner/inspections/", {"product_name": "Test Tea"}, format="json")
        self.assertEqual(created.status_code, 201)
        inspection_id = created.data["inspection_id"]
        for index in range(2):
            response = self.client.post(
                f"/api/scanner/inspections/{inspection_id}/images/",
                {"image": image_file(f"label-{index}.png"), "image_type": "FRONT"},
                format="multipart",
            )
            self.assertEqual(response.status_code, 201)
        self.client.force_authenticate(self.other_user)
        self.assertEqual(self.client.get(f"/api/scanner/inspections/{inspection_id}/").status_code, 404)

    def test_invalid_image_is_rejected(self):
        created = self.client.post("/api/scanner/inspections/", {}, format="json")
        response = self.client.post(
            f"/api/scanner/inspections/{created.data['inspection_id']}/images/",
            {"image": SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)


class ExtractionServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="processing_user", password="TestPassword@123")
        self.inspection = Inspection.objects.create(officer=self.user)

    def test_valid_image_passes_preprocessing(self):
        image = InspectionImage.objects.create(
            inspection=self.inspection,
            image=image_file(),
            original_filename="label.png",
            file_size=1,
        )
        result = process_image(image)
        self.assertTrue(result["ok"])
        self.assertEqual(result["image"].processing_status, "PREPROCESSED")

    def test_extracts_common_package_fields_without_compliance_decisions(self):
        values, metadata = extract_fields("MRP Rs. 120\nNet Qty 500 g\nCountry of Origin: India")
        self.assertEqual(values["mrp"], "120")
        self.assertEqual(values["quantity_unit"], "g")
        self.assertEqual(values["country_of_origin"], "India")
        self.assertEqual(metadata["mrp"]["status"], "DETECTED")
        self.assertNotIn("compliant", values)
