# Generated by Django 5.1.4 on 2025-01-30 21:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('tipo_sangre', models.CharField(max_length=3)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contrasenia', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='PersonaImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asociacion', models.DateTimeField(auto_now_add=True)),
                ('imagen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personas', to='database.imagen')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='database.persona')),
            ],
        ),
    ]
