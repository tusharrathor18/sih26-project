from io import BytesIO

from django.core.files.base import ContentFile

from scanner.models import InspectionImage


def process_image(image_record: InspectionImage):
    """Create an OCR-ready copy and basic quality metadata without changing the original."""
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageStat

        image_record.image.seek(0)
        original = Image.open(image_record.image).convert("RGB")
        width, height = original.size
        image_record.width = width
        image_record.height = height

        grayscale = original.convert("L")
        brightness = ImageStat.Stat(grayscale).mean[0]
        contrast = ImageStat.Stat(grayscale).stddev[0]
        quality_score = min(1.0, max(0.0, (min(width, height) / 1200) * 0.5 + min(contrast / 64, 1.0) * 0.5))
        image_record.quality_score = round(quality_score, 3)
        image_record.quality_warning = ""
        if min(width, height) < 600:
            image_record.quality_warning = "Low resolution; text recognition may be inaccurate."
        elif brightness < 35 or brightness > 235 or contrast < 12:
            image_record.quality_warning = "Low contrast or extreme brightness; text recognition may be inaccurate."

        processed = grayscale.filter(ImageFilter.MedianFilter(size=3))
        processed = ImageEnhance.Contrast(processed).enhance(1.35)
        try:
            import cv2
            import numpy as np

            cv_image = np.array(processed)
            cv_image = cv2.fastNlMeansDenoising(cv_image, None, 7, 7, 21)
            cv_image = cv2.detailEnhance(cv2.cvtColor(cv_image, cv2.COLOR_GRAY2BGR), sigma_s=10, sigma_r=0.15)
            processed = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY))
        except ImportError:
            pass
        output = BytesIO()
        processed.save(output, format="PNG", optimize=True)
        image_record.processed_image.save(
            f"{image_record.original_filename.rsplit('.', 1)[0]}.png",
            ContentFile(output.getvalue()),
            save=False,
        )
        image_record.processing_status = "PREPROCESSED"
        image_record.save(update_fields=[
            "processed_image", "width", "height", "quality_score",
            "quality_warning", "processing_status",
        ])
        return {"ok": True, "image": image_record}
    except Exception as exc:
        image_record.processing_status = "FAILED"
        image_record.quality_warning = "Image preprocessing failed."
        image_record.save(update_fields=["processing_status", "quality_warning"])
        return {"ok": False, "error": str(exc), "image": image_record}
