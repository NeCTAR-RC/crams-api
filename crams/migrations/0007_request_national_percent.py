# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0006_insert_nectar_notificationtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='national_percent',
            field=models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], default=100),
        ),
    ]
