# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0009_request_national_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationtemplate',
            name='alert_funding_body',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='fundingbody',
            name='email',
            field=models.EmailField(max_length=254, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grant',
            name='duration',
            field=models.IntegerField(error_messages={'min_value': 'Please enter funding duration (in months 1-1000).', 'max_value': 'Please enter funding duration (in months 1~1000).'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)]),
        ),
    ]
