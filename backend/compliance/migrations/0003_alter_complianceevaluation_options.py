from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("compliance", "0002_version_evaluations")]

    operations = [
        migrations.AlterModelOptions(
            name="complianceevaluation",
            options={"ordering": ["-evaluation_version"]},
        ),
    ]
