# Generated by Django 3.2.2 on 2024-08-01 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oss', '0007_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='correction_due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
