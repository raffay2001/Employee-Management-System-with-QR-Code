# Generated by Django 2.2.10 on 2021-09-29 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0010_auto_20210929_1201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='designatioin',
            new_name='designation',
        ),
    ]