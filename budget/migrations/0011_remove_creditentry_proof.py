# Generated by Django 3.1.1 on 2020-11-28 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0010_creditentry_proof'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creditentry',
            name='proof',
        ),
    ]
