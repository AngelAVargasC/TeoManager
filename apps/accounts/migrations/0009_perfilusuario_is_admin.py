# Generated by Django 5.2 on 2025-05-01 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_remove_imagenproducto_producto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
