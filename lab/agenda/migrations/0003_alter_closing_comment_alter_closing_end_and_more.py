# Generated by Django 4.0.7 on 2023-01-27 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0041_alter_call_status'),
        ('agenda', '0002_alter_closing_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closing',
            name='comment',
            field=models.TextField(null=True, verbose_name='agenda:cosing:attribute:comment'),
        ),
        migrations.AlterField(
            model_name='closing',
            name='end',
            field=models.DateTimeField(db_index=True, verbose_name='agenda:closing:attribute:end'),
        ),
        migrations.AlterField(
            model_name='closing',
            name='is_global',
            field=models.BooleanField(verbose_name='agenda:cosing:attribute:is_global'),
        ),
        migrations.AlterField(
            model_name='closing',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.location', verbose_name='agenda:closing:attribute:location'),
        ),
        migrations.AlterField(
            model_name='closing',
            name='start',
            field=models.DateTimeField(db_index=True, verbose_name='agenda:closing:attribute:start'),
        ),
    ]