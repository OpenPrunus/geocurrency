# Generated by Django 3.2 on 2021-04-18 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0003_auto_20201019_0725'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customunit',
            options={'ordering': ['name', 'code']},
        ),
        migrations.AlterField(
            model_name='customunit',
            name='alias',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Other code for this unit (e.g.: mybu)'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='code',
            field=models.SlugField(verbose_name='technical name of the unit (e.g.: myUnit)'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='key',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=255, null=True, verbose_name='Categorization field (e.g.: customer ID)'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Human readable name (e.g.: My Unit)'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='relation',
            field=models.CharField(max_length=255, verbose_name='Relation to an existing unit (e.g.: 12 kg*m/s)'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='symbol',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Symbol to use in a formula (e.g.: myu)'),
        ),
        migrations.AlterField(
            model_name='customunit',
            name='unit_system',
            field=models.CharField(choices=[('Planck', 'Planck'), ('SI', 'SI'), ('US', 'US'), ('atomic', 'atomic'), ('cgs', 'CGS'), ('imperial', 'imperial'), ('mks', 'mks')], max_length=20, verbose_name='Unit system to register the unit in'),
        ),
    ]
