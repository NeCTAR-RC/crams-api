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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('data', models.TextField()),
                ('contact', models.ForeignKey(to='crams.Contact', blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='provisiondetails',
            name='status',
            field=models.CharField(choices=[('S', 'Sent'), ('P', 'Provisioned'), ('F', 'Failed'), ('L', 'Resend'), ('U', 'Updated'), ('X', 'Update Sent')], max_length=1, default='S'),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='project',
            field=models.ForeignKey(to='crams.Project', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='request',
            field=models.ForeignKey(to='crams.Request', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='internalmigrationdata',
            name='system',
            field=models.ForeignKey(to='crams.ProjectIDSystem'),
        ),
    ]
