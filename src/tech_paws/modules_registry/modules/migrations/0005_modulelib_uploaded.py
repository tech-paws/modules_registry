# Generated by Django 3.1.7 on 2021-03-28 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0004_auto_20210328_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulelib',
            name='uploaded',
            field=models.BooleanField(default=False),
        ),
    ]
