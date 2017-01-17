# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0008_update_grant_model'),
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
    ]
