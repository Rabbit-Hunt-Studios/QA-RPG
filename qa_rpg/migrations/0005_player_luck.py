# Generated by Django 4.1.2 on 2022-10-22 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa_rpg', '0004_player_activity_player_dungeon_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='luck',
            field=models.FloatField(default=0.2),
        ),
    ]
