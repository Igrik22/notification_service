# Generated by Django 4.0.3 on 2022-03-22 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='tag',
        ),
        migrations.AddField(
            model_name='client',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, related_name='clients', to='core.tag', verbose_name='тэг(произвольная метка)'),
        ),
    ]
