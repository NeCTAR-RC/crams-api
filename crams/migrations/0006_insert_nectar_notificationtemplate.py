# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_nectar_notification_data_from_sql():
    from crams.settings import BASE_DIR
    import os

    file_name = 'crams/sql/nectar_notifications.sql'

    sql_statements = open(os.path.join(BASE_DIR, file_name), 'r').read()

    return sql_statements


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('crams', '0005_auto_20160825_1933'),
    ]

    operations = [
        migrations.RunSQL(load_nectar_notification_data_from_sql()),
    ]
