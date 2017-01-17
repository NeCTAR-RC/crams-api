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
            name='allocation_node',
            field=models.ForeignKey(blank=True, related_name='requests', to='crams.AllocationHome', null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='national_percent',
            field=models.PositiveSmallIntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100)]),
        ),
    ]
