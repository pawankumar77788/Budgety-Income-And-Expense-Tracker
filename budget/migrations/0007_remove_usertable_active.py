# Generated by Django 3.1.1 on 2020-11-10 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0006_usertable_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertable',
            name='active',
        ),
    ]
