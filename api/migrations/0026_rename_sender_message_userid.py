# Generated by Django 5.1.2 on 2024-12-08 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_rename_waranty_product_warranty'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='sender',
            new_name='userID',
        ),
    ]
