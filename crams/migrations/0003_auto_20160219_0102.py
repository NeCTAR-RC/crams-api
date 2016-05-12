# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def load_forcode_data_from_sql():
    from crams.settings import BASE_DIR

    import os

    sql_statements = open(os.path.join(BASE_DIR,
                                       'crams/sql/forcode.sql'), 'r').read()

    return sql_statements

class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0002_auto_20160218_0650'),
    ]

    operations = [
        migrations.RunSQL(load_forcode_data_from_sql()),
    ]
