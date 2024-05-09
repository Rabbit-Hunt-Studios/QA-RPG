"""Module containing models for storing data in database."""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_cryptography.fields import encrypt

BASE_LUCK = 0.25
BASE_HEALTH = 100


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = encrypt(models.EmailField())
    first_name = encrypt(models.CharField(max_length=200))
    last_name = encrypt(models.CharField(max_length=200))
    policy = models.BooleanField(default=True)


class Question(models.Model):
    """Question model for creating questions."""

    question_text = models.CharField(max_length=200)
    damage = models.IntegerField(default=20)
    currency = models.IntegerField(default=0)
    max_currency = models.IntegerField(default=20)
    rate = models.IntegerField(default=5)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, null=False, default="test")
    enable = models.BooleanField(default=True)

    @property
    def report(self):
        """Get amount of reports this question has."""
        return ReportAndCommend.objects.filter(question=self, vote=0).count()

    @property
    def commend(self):
        """Get amount of commends this question has."""
        return ReportAndCommend.objects.filter(question=self, vote=1).count()

    @property
    def correct_choice(self):
        """Get the correct answer of this question."""
        return Choice.objects.get(question=self, correct_answer=True)

    def add_coin(self):
        """Add coins to question for owner to collect."""
        if self.currency + self.rate <= self.max_currency:
            self.currency += self.rate
            self.save()

    def __str__(self):
        """Return Question string."""
        return self.question_text


class Choice(models.Model):
    """Choice model for creating choices."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct_answer = models.BooleanField()

    def __str__(self):
        """Return Choice string."""
        return self.choice_text


class ReportAndCommend(models.Model):
    """Report and Commend model for creating reports or commends."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField()


class Player(models.Model):
    """Player model for creating players."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    max_hp = models.IntegerField(default=BASE_HEALTH)
    current_hp = models.IntegerField(default=BASE_HEALTH)
    currency = models.IntegerField(default=0)
    dungeon_currency = models.IntegerField(default=0)
    activity = models.CharField(max_length=100, default="index")
    luck = models.FloatField(default=BASE_LUCK)
    awake = models.IntegerField(default=0)
    question_max_currency = models.IntegerField(default=20)
    question_rate_currency = models.IntegerField(default=5)
    status = models.CharField(max_length=50, default="")

    @property
    def player_name(self):
        """Return username of this player."""
        return self.user.username

    def update_player_stats(self, health: int = 0, dungeon_currency: int = 0, luck: float = 0):
        """Add values to stats of player."""
        self.current_hp += health
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        self.dungeon_currency += dungeon_currency
        self.luck += luck
        self.save()

    def reset_stats(self):
        """Reset player's health to max and other stats to zero or empty."""
        self.current_hp = self.max_hp
        self.luck = BASE_LUCK
        self.dungeon_currency = 0
        self.status = ""
        self.save()

    def add_dungeon_currency(self):
        """Transfer coins from dungeon to main storage."""
        self.currency += self.dungeon_currency
        self.dungeon_currency = 0
        self.save()

    def set_activity(self, activity: str):
        """Set player activity."""
        self.activity = activity
        self.save()

    def check_death(self):
        """Check player's current health, if below zero, clear dungeon coins and inventory."""
        if self.current_hp <= 0:
            self.set_activity("index")
            self.reset_stats()
            Inventory.objects.get(player=self).clear_dungeon_inventory()
            self.save()
            return True
        return False


class Log(models.Model):
    """Log model for creating logs."""

    log_text = models.CharField(max_length=1000, default=";;;;;;;;;;")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    log_questions = models.CharField(max_length=1000, default="")
    log_report_question = models.CharField(max_length=1000, default="")

    def split_log(self, log_type):
        """Return list form of a log in accordance to the type inputted."""
        if log_type == "text":
            return self.log_text.split(';')[:-1]
        if log_type == "question":
            return self.log_questions.split(';')[:-1]
        return self.log_report_question.split(';')[:-1]

    def clear_log(self):
        """Clear log to be empty."""
        self.log_text = ";;;;;;;;;;"
        self.save()

    def clear_question(self):
        """Clear seen questions to be none."""
        self.log_questions = ""
        self.save()

    def add_log(self, text):
        """Add new player action log."""
        list_log = self.log_text.split(';')
        del (list_log[0])
        self.log_text = ";".join(list_log)
        self.log_text += f"{text};"
        self.save()

    def add_question(self, question_id: str):
        """Add seen question id to log."""
        self.log_questions += f"{question_id};"
        if len(self.split_log('question')) > 100:
            self.clear_question()
        self.save()

    def remove_question(self, question_id: str):
        """Remove seen_question id from log."""
        seen_question = self.split_log("question")
        if question_id in seen_question:
            seen_question.remove(question_id)
            self.log_questions = f"{';'.join(seen_question)}" + ";"
        self.save()

    def add_report_question(self, question_id: int):
        """Add player's reported question to log."""
        if str(question_id) not in self.split_log("report"):
            self.log_report_question += f"{question_id};"
        self.save()

    def __str__(self):
        """Return Log string."""
        return self.log_text


class Inventory(models.Model):
    """Inventory model for creating inventory."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_inventory = models.CharField(max_length=1000, default="")
    dungeon_inventory = models.CharField(max_length=1000, default="")
    max_inventory = models.IntegerField(default=3)
    question_template = models.CharField(max_length=1000, default="")

    def get_inventory(self, inventory_type):
        """Return dict of inventory."""
        dict_item = {}
        if inventory_type == "player":
            inventory = self.player_inventory.split(';')[:-1]
        else:
            inventory = self.dungeon_inventory.split(';')[:-1]
        for item in inventory:
            item_list = item.split(":")
            dict_item[int(item_list[0])] = int(item_list[1])
        return dict_item

    def update_inventory(self, item: dict, inventory_type):
        """Update item into inventory."""
        inventory = ""
        for key, val in item.items():
            if val > 0:
                inventory += f"{key}:{val};"
        if inventory_type == "player":
            self.player_inventory = inventory
        else:
            self.dungeon_inventory = inventory
        self.save()

    def clear_dungeon_inventory(self):
        """Clear dungeon inventory."""
        self.dungeon_inventory = ""
        self.save()

    def reset_inventory(self):
        """Move items from dungeon inventory to player inventory."""
        p_inventory = self.get_inventory("player")
        d_inventory = self.get_inventory("dungeon")
        for item, amount in d_inventory.items():
            if item in p_inventory:
                p_inventory[item] += amount
            else:
                p_inventory[item] = amount
        self.update_inventory(p_inventory, "player")
        self.clear_dungeon_inventory()

    def get_templates(self):
        """Return dict of player templates."""
        owned = {}
        for value in self.question_template.split(';')[:-1]:
            value = value.split(":")
            owned[int(value[0])] = int(value[1])
        return owned

    def update_templates(self, items: dict):
        """Update templates into inventory."""
        item_string = ""
        for key, value in items.items():
            if value > 0:
                item_string += f"{key}:{value};"
        self.question_template = item_string
        self.save()
