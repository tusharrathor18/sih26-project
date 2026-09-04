from django.db import models

# Models for Legal Metrology Rules, Compliance Results, and Violations
# will be built in Prompt 2+.
# Foundation design:
# class ComplianceEvaluation(models.Model):
#     inspection = models.OneToOneField('scanner.Inspection', on_delete=models.CASCADE)
#     overall_status = models.CharField(...) # PASS, FAIL, WARNING, MANUAL_REVIEW
#     evaluated_at = models.DateTimeField(auto_now_add=True)
