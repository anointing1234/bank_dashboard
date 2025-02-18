# Generated by Django 5.0.7 on 2025-02-16 12:35

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_transfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfercode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transfercode',
            name='expires_at',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Code expiration time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transfercode',
            name='used',
            field=models.BooleanField(default=False, help_text='Has the code been used?'),
        ),
        migrations.AddField(
            model_name='transfercode',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transfer_codes',
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transfercode',
            name='transfer_code',
            field=models.CharField(help_text='Code for transfers', max_length=10, unique=True),
        ),
    ]
