# Generated by Django 4.2.16 on 2024-12-03 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheema_retail_store', '0004_alter_product_images_urls'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='title',
            new_name='name',
        ),
    ]