# Generated by Django 3.2.25 on 2024-09-17 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oss', '0011_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='additional_file',
            field=models.FileField(blank=True, null=True, upload_to='submissions/'),
        ),
        migrations.AddField(
            model_name='submission',
            name='copyright_file',
            field=models.FileField(blank=True, null=True, upload_to='submissions/'),
        ),
        migrations.AddField(
            model_name='submission',
            name='plag_report',
            field=models.FileField(blank=True, null=True, upload_to='submissions/'),
        ),
    ]
