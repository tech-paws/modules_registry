# Generated by Django 3.1.7 on 2021-03-28 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0005_modulelib_uploaded'),
    ]

    operations = [
        migrations.RenameField(
            model_name='moduleversion',
            old_name='is_published',
            new_name='published',
        ),
    ]
