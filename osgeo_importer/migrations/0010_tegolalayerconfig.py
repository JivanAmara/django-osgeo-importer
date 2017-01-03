# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osgeo_importer', '0009_mapproxycacheconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='TegolaLayerConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('config', models.TextField()),
                ('layer', models.OneToOneField(to='osgeo_importer.UploadLayer')),
            ],
        ),
    ]
