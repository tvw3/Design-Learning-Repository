# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration_login', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='security_answer',
            field=models.CharField(null=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='security_question',
            field=models.CharField(max_length=7, choices=[('teacher', 'What was the last name of your favorite grade teacher?'), ('book', 'What was the first book you ever read?'), ('pet', 'What was the name of your first pet?'), ('father', 'In what city was your father born?'), ('mother', 'In what city was your mother born?'), ('car', 'What was the color of your first car?')], default='pet'),
        ),
    ]
