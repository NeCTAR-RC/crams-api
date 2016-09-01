# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0004_auto_20160607_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('template_file_path', models.CharField(max_length=99)),
                ('funding_body', models.ForeignKey(related_name='notification_templates', to='crams.FundingBody')),
                ('request_status', models.ForeignKey(to='crams.RequestStatus')),
            ],
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='notificationtemplate',
            unique_together=set([('funding_body', 'request_status')]),
        ),
    ]
