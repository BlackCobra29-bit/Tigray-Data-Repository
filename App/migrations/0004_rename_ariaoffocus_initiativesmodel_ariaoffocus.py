# Generated by Django 5.1.1 on 2024-11-22 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_rename_focusofaria_initiativesmodel_ariaoffocus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='initiativesmodel',
            old_name='AriaofFocus',
            new_name='AriaOfFocus',
        ),
    ]