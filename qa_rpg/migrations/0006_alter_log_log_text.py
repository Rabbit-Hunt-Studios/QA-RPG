# Generated by Django 4.1 on 2022-10-22 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qa_rpg", "0005_player_luck"),
    ]

    operations = [
        migrations.AlterField(
            model_name="log",
            name="log_text",
            field=models.CharField(default=";;;;;;;;;;", max_length=1000),
        ),
    ]