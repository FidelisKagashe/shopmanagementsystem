# Generated by Django 5.1.2 on 2025-03-08 21:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_purchaseorder_total_amount'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CashBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('cash', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('bank', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('CR', 'Credit (Cash In)'), ('DR', 'Debit (Cash Out)')], max_length=2)),
                ('source', models.CharField(choices=[('SALE', 'Sale Order'), ('PURCHASE', 'Purchase Order'), ('FINANCIAL', 'Financial Transaction')], max_length=10)),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='saleorder',
            name='payment_status',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Bank', 'Bank')], default='Unpaid', max_length=100),
        ),
        migrations.CreateModel(
            name='UserFinancialTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('ADD', 'Addition'), ('REMOVE', 'Removal')], max_length=6)),
                ('account', models.CharField(choices=[('CASH', 'Cash'), ('BANK', 'Bank')], default='CASH', max_length=4)),
                ('approved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
