# Generated by Django 4.0.6 on 2022-08-15 10:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sdcpeople', '0030_peoplelist_listmembership'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PeopleList',
            new_name='SavedList',
        ),
        migrations.AlterModelOptions(
            name='listmembership',
            options={'ordering': ('savedlist',)},
        ),
        migrations.RenameField(
            model_name='listmembership',
            old_name='peoplelist',
            new_name='savedlist',
        ),
    ]