from django.db import models
from django.contrib.auth.models import User

class OfficerProfile(models.Model):
    """
    Stores professional and jurisdictional metadata for Legal Metrology officers.
    Tied one-to-one with the Django User authentication model.
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Department Administrator'),
        ('INSPECTOR', 'Legal Metrology Inspector'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='officer_profile',
        verbose_name='Auth User'
    )
    officer_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Unique official ID issued to the officer (e.g., OFF-DEL-2024-001)'
    )
    name = models.CharField(
        max_length=150,
        help_text='Official full name of the officer'
    )
    designation = models.CharField(
        max_length=100,
        help_text='Official designation (e.g., Senior Inspector of Legal Metrology)'
    )
    department = models.CharField(
        max_length=200,
        default='Department of Consumer Affairs, Legal Metrology Division',
        help_text='Department or directorate'
    )
    jurisdiction = models.CharField(
        max_length=150,
        help_text='Jurisdiction or assigned enforcement zone (e.g., Zone-1, Central Delhi)'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='INSPECTOR',
        help_text='Role defining system permissions'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Official contact phone number'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this officer profile is authorized to perform inspections'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Officer Profile'
        verbose_name_plural = 'Officer Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.officer_id} — {self.name} ({self.get_role_display()})"
