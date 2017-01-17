# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationhome',
            name='code',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='grant',
            name='start_year',
            field=models.IntegerField(default=2017, error_messages={'max_value': 'Please input a year between 1970 ~ 3000', 'min_value': 'Please input a year between 1970 ~ 3000'}, validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)]),
        ),
    ]
