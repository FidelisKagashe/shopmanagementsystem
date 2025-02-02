# Generated by Django 5.1.2 on 2025-01-27 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dawa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jina', models.CharField(max_length=200, verbose_name='Jina la Dawa')),
                ('maelezo', models.TextField(blank=True, verbose_name='Maelezo ya Dawa')),
                ('bei', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Bei ya Dawa')),
                ('picha', models.ImageField(blank=True, null=True, upload_to='dawa_picha/', verbose_name='Picha ya Dawa')),
            ],
            options={
                'verbose_name': 'Dawa',
                'verbose_name_plural': 'Dawa',
                'ordering': ['jina'],
            },
        ),
    ]
