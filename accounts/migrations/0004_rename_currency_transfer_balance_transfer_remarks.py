# Generated by Django 5.0.7 on 2025-02-28 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_beneficiary_bank_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transfer',
            old_name='currency',
            new_name='balance',
        ),
        migrations.AddField(
            model_name='transfer',
            name='remarks',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
