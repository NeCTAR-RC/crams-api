# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0008_request_national_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='duration',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)], default=12, error_messages={'max_value': 'Please input a year between 0 ~ 1000', 'min_value': 'Please input a year between 0 ~ 1000'}),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='grant',
            name='grant_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='grant',
            name='start_year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)], default=2017, error_messages={'max_value': 'Please input a year between 1970 ~ 3000', 'min_value': 'Please input a year between 1970 ~ 3000'}),
        ),
    ]
