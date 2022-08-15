# Generated by Django 4.0.6 on 2022-08-14 17:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sdcpeople', '0028_bulkcommunication_communicationresult_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='communicationevent',
            options={'ordering': ['-when']},
        ),
        migrations.AddField(
            model_name='communicationevent',
            name='result',
            field=models.ForeignKey(help_text='The result of this communication', null=True, on_delete=django.db.models.deletion.SET_NULL, to='sdcpeople.communicationresult'),
        ),
        migrations.AlterField(
            model_name='communicationresult',
            name='name',
            field=models.CharField(blank=True, help_text='The name of the bulk action', max_length=100, verbose_name='name'),
        ),
    ]
