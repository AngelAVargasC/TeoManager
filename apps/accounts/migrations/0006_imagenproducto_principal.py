# Generated by Django 5.2 on 2025-04-27 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_producto_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagenproducto',
            name='principal',
            field=models.BooleanField(default=False),
        ),
    ]
