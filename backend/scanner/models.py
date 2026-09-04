from django.db import models
from users.models import OfficerProfile

# Models for Scanner, Product, and Image Sessions will be built in Prompt 2+.
# Foundation design:
# class Inspection(models.Model):
#     officer = models.ForeignKey(OfficerProfile, on_delete=models.PROTECT, related_name='inspections')
#     commodity_name = models.CharField(max_length=255)
#     scan_session_id = models.CharField(max_length=100, unique=True)
#     status = models.CharField(...)
#     created_at = models.DateTimeField(auto_now_add=True)
