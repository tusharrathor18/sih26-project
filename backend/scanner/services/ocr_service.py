import importlib

from scanner.models import InspectionImage, OCRResult


def run_ocr(image_record: InspectionImage):
    """Run PaddleOCR when installed and preserve text, confidence, and boxes."""
    ocr_result, _ = OCRResult.objects.get_or_create(image=image_record)
    try:
        if not importlib.util.find_spec("paddleocr"):
            raise RuntimeError("PaddleOCR is not installed in the backend environment.")

        from paddleocr import PaddleOCR

        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        source = image_record.processed_image.path if image_record.processed_image else image_record.image.path
        result = ocr.ocr(source, cls=True)
        regions = []
        text_parts = []
        confidences = []
        for page in result or []:
            for line in page or []:
                if len(line) < 2:
                    continue
                box, value = line
                text, confidence = value
                regions.append({"text": text, "confidence": float(confidence), "bounding_box": box})
                text_parts.append(text)
                confidences.append(float(confidence))

        ocr_result.raw_text = "\n".join(text_parts)
        ocr_result.regions = regions
        ocr_result.average_confidence = sum(confidences) / len(confidences) if confidences else None
        ocr_result.engine = "PaddleOCR"
        ocr_result.engine_version = getattr(importlib.import_module("paddleocr"), "__version__", "unknown")
        ocr_result.error_message = ""
        image_record.processing_status = "OCR_COMPLETE"
        image_record.save(update_fields=["processing_status"])
    except Exception as exc:
        ocr_result.error_message = "OCR processing is unavailable or failed."
        ocr_result.engine = "PaddleOCR"
        image_record.processing_status = "OCR_FAILED"
        image_record.save(update_fields=["processing_status"])
    ocr_result.save()
    return ocr_result
