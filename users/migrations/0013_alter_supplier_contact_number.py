# Generated by Django 5.1.2 on 2025-03-09 20:27

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_delete_cashbook_purchaseorder_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='contact_number',
            field=models.CharField(blank=True, max_length=20, null=True, validators=[users.models.validate_contact_number]),
        ),
    ]
