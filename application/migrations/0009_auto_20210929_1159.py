# Generated by Django 2.2.10 on 2021-09-29 06:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0008_auto_20210929_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='member_since',
            field=models.DateField(default=datetime.datetime(2021, 9, 29, 11, 59, 18, 209504)),
        ),
    ]