# Generated by Django 4.0.3 on 2022-03-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sdcpeople', '0018_alter_person_options_personuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='name_prefix',
            field=models.CharField(blank=True, help_text="The person's name prefix or title", max_length=10, verbose_name='prefix'),
        ),
        migrations.AddField(
            model_name='person',
            name='name_suffix',
            field=models.CharField(blank=True, help_text="The person's name suffix", max_length=10, verbose_name='suffix'),
        ),
    ]
