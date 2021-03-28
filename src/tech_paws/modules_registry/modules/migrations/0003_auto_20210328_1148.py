# Generated by Django 3.1.7 on 2021-03-28 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0002_modulelib'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulelib',
            name='os',
            field=models.CharField(default='linux', max_length=255),
        ),
        migrations.AddField(
            model_name='moduleversion',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]
