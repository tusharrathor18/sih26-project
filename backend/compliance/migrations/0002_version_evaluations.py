from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("compliance", "0001_initial"), ("scanner", "0003_fieldcorrection_auditlog")]
    operations = [
        migrations.AlterField(model_name="complianceevaluation", name="inspection", field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="compliance_evaluations", to="scanner.inspection")),
        migrations.AddField(model_name="complianceevaluation", name="evaluation_version", field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name="complianceevaluation", name="is_current", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="complianceevaluation", name="superseded_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddConstraint(model_name="complianceevaluation", constraint=models.UniqueConstraint(fields=("inspection", "evaluation_version"), name="unique_inspection_evaluation_version")),
    ]
