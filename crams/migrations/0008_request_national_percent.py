# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0007_update_compute_request_min_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='allocation_home',
            field=models.ForeignKey(related_name='requests', blank=True, to='crams.AllocationHome', null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='national_percent',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(100)], default=100),
        ),
        migrations.AlterField(
            model_name='allocationhome',
            name='code',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='grant',
            name='start_year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)], default=2017, error_messages={'min_value': 'Please input a year between 1970 ~ 3000', 'max_value': 'Please input a year between 1970 ~ 3000'}),
        ),
    ]
