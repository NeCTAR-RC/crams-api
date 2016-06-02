# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0003_auto_20160219_0102'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalMigrationData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('data', models.TextField()),
                ('contact', models.ForeignKey(null=True, to='crams.Contact', blank=True)),
                ('project', models.ForeignKey(to='crams.Project')),
                ('request', models.ForeignKey(null=True, to='crams.Request', blank=True)),
                ('system', models.ForeignKey(to='crams.ProjectIDSystem')),
            ],
        ),
        migrations.AlterField(
            model_name='provisiondetails',
            name='status',
            field=models.CharField(default='S', max_length=1, choices=[('S', 'Sent'), ('P', 'Provisioned'), ('F', 'Failed'), ('L', 'Resend'), ('U', 'Updated'), ('X', 'Update Sent')]),
        ),
    ]
