# Generated by Django 3.2.2 on 2024-08-01 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dl', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='description',
            field=models.CharField(max_length=255, verbose_name='Month'),
        ),
    ]
