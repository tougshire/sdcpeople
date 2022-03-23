# Generated by Django 4.0.3 on 2022-03-22 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sdcpeople', '0009_alter_contactvoice_options_alter_position_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contacttext',
            options={'ordering': ['-rank_number', 'number']},
        ),
        migrations.RemoveField(
            model_name='contacttext',
            name='is_primary',
        ),
        migrations.RemoveField(
            model_name='contactvoice',
            name='is_primary',
        ),
        migrations.AddField(
            model_name='contacttext',
            name='label',
            field=models.CharField(blank=True, help_text='The label for this phone, such as "Work" or "Home"', max_length=50, verbose_name='label'),
        ),
        migrations.AddField(
            model_name='contacttext',
            name='rank_number',
            field=models.IntegerField(default=0, help_text='A number representing the placement of this phone on a list in descending order (ex: if you want this one first, give it a high number like 1000)', verbose_name='rank'),
        ),
    ]