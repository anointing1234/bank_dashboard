# Generated by Django 5.0.7 on 2025-02-15 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_account_account_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='reference_code',
        ),
        migrations.AddField(
            model_name='transaction',
            name='from_account',
            field=models.CharField(blank=True, help_text='Debit account or source of funds', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='institution',
            field=models.CharField(blank=True, help_text='Institution involved in the transaction', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='reference',
            field=models.CharField(blank=True, help_text='Optional unique reference for the transaction', max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='region',
            field=models.CharField(blank=True, help_text='Region where the transaction occurred', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='to_account',
            field=models.CharField(blank=True, help_text='Credit account or destination of funds', max_length=100, null=True),
        ),
    ]
