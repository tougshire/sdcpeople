# Generated by Django 4.0.3 on 2022-03-22 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sdcpeople', '0010_alter_contacttext_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='votingaddress',
            old_name='locationmagestrate',
            new_name='locationmagistrate',
        ),
    ]
