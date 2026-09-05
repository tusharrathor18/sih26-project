from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("scanner", "0001_initial")]
    operations = [
        migrations.AddField(model_name="inspection", name="commodity_category", field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name="inspection", name="package_type", field=models.CharField(blank=True, max_length=40)),
        migrations.AddField(model_name="inspection", name="consumer_type", field=models.CharField(blank=True, max_length=40)),
        migrations.AddField(model_name="inspection", name="approximate_quantity", field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
        migrations.AddField(model_name="inspection", name="quantity_unit", field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name="inspection", name="actual_measured_quantity", field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
        migrations.AddField(model_name="inspection", name="measurement_unit", field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name="inspection", name="measurement_method", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="inspection", name="sample_size", field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="inspection", name="lot_size", field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="inspection", name="observed_deficiency", field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
    ]
