# Generated by Django 5.2 on 2025-04-27 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_producto_categoria_producto_imagen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='servicios/'),
        ),
    ]
