# Generated by Django 5.0.7 on 2025-02-28 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiary',
            name='bank_address',
            field=models.CharField(blank=True, help_text="The physical address of the beneficiary's bank.", max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='beneficiary',
            name='routing_transit_number',
            field=models.CharField(blank=True, help_text='A 9-digit code used to identify the bank in US transactions.', max_length=9, null=True),
        ),
    ]
