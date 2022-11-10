from django.db import models
from django.contrib.auth.models import User

BASE_LUCK = 0.25
BASE_HEALTH = 100


class Question(models.Model):
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
        return ReportAndCommend.objects.filter(question=self, vote=0).count()

    @property
    def commend(self):
        return ReportAndCommend.objects.filter(question=self, vote=1).count()

    @property
    def correct_choice(self):
        return Choice.objects.get(question=self, correct_answer=True)

    def add_coin(self):
        if self.currency + self.rate <= self.max_currency:
            self.currency += self.rate
            self.save()

    def __str__(self):
        """Return Question string."""
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    correct_answer = models.BooleanField()

    def __str__(self):
        """Return Choice string."""
        return self.choice_text


class ReportAndCommend(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField()


class Player(models.Model):
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
        return self.user.username

    def update_player_stats(self, health: int = 0, dungeon_currency: int = 0, luck: float = 0):
        self.current_hp += health
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        self.dungeon_currency += dungeon_currency
        self.luck += luck
        self.save()

    def reset_stats(self):
        self.current_hp = self.max_hp
        self.luck = BASE_LUCK
        self.dungeon_currency = 0
        self.save()

    def add_dungeon_currency(self):
        self.currency += self.dungeon_currency
        self.dungeon_currency = 0
        self.save()

    def set_activity(self, activity: str):
        self.activity = activity
        self.save()

    def check_death(self):
        if self.current_hp <= 0:
            self.set_activity("index")
            self.reset_stats()
            try:
                Log.objects.get(player=self).clear_log()
            except Log.DoesNotExist:
                Log.objects.create(player=self)
            self.save()
            return True
        return False


class Log(models.Model):
    log_text = models.CharField(max_length=1000, default=";;;;;;;;;;")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    log_questions = models.CharField(max_length=1000, default="")
    log_report_question = models.CharField(max_length=1000, default="")

    def split_log(self, log_type):
        if log_type == "text":
            return self.log_text.split(';')[:-1]
        elif log_type == "question":
            return self.log_questions.split(';')[:-1]
        elif log_type == "report":
            return self.log_report_question.split(';')[:-1]

    def clear_log(self):
        self.log_text = ";;;;;;;;;;"
        self.save()

    def clear_question(self):
        self.log_questions = ""
        self.save()

    def add_log(self, text):
        list_log = self.log_text.split(';')
        del (list_log[0])
        self.log_text = ";".join(list_log)
        self.log_text += f"{text};"
        self.save()

    def add_question(self, question_id: str):
        self.log_questions += f"{question_id};"
        if len(self.split_log('question')) > 100:
            self.clear_question()
        self.save()

    def add_report_question(self, question_id: int):
        if str(question_id) not in self.split_log("report"):
            self.log_report_question += f"{question_id};"
        self.save()

    def __str__(self):
        """Return Log string."""
        return self.log_text


class Inventory(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_inventory = models.CharField(max_length=1000, default="")
    dungeon_inventory = models.CharField(max_length=1000, default="")
    max_inventory = models.IntegerField(default=2)
    question_template = models.CharField(max_length=1000, default="")

    def get_inventory(self, inventory_type):
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
        self.dungeon_inventory = ""
        self.save()

    def reset_inventory(self):
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
        owned = {}
        for value in self.question_template.split(';')[:-1]:
            value = value.split(":")
            owned[int(value[0])] = int(value[1])
        return owned

    def update_templates(self, items: dict):
        item_string = ""
        for key, value in items.items():
            if value > 0:
                item_string += f"{key}:{value};"
        self.question_template = item_string
        self.save()
