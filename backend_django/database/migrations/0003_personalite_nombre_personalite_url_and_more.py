# Generated by Django 5.1.4 on 2025-02-02 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_personalite'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalite',
            name='nombre',
            field=models.CharField(default='Nombre predeterminado', max_length=50),
        ),
        migrations.AddField(
            model_name='personalite',
            name='url',
            field=models.URLField(default='https://www.google.com', max_length=500),
        ),
        migrations.AlterField(
            model_name='personalite',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
