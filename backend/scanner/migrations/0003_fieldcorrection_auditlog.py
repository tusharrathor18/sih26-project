from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("scanner", "0002_inspection_compliance_inputs"), ("users", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="FieldCorrection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("field_name", models.CharField(max_length=100)),
                ("original_value", models.TextField(blank=True)),
                ("corrected_value", models.TextField(blank=True)),
                ("correction_reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("corrected_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="inspection_corrections", to="auth.user")),
                ("inspection", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="corrections", to="scanner.inspection")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=50)),
                ("description", models.TextField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("previous_value", models.TextField(blank=True)),
                ("new_value", models.TextField(blank=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("inspection", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit_logs", to="scanner.inspection")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="inspection_audit_logs", to="auth.user")),
            ],
            options={"ordering": ["timestamp"]},
        ),
    ]
