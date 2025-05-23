# Generated by Django 5.2 on 2025-05-01 01:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_perfilusuario_is_admin'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfilusuario',
            name='is_admin',
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='permisos',
            field=models.CharField(choices=[('Usuario', 'Usuario'), ('Administrador', 'Administrador')], default='Usuario', max_length=20),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='usuario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL),
        ),
    ]
