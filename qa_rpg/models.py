from django.db import models
from django.contrib.auth.models import User

BASE_LUCK = 0.25
BASE_HEALTH = 100


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    damage = models.IntegerField(default=20)
    currency = models.IntegerField(default=0)
    max_currency = models.IntegerField(default=20)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, null=False, default="test")
    enable = models.BooleanField(default=True)

    @property
    def report(self):
        return Report.objects.filter(question=self).count()

    @property
    def commend(self):
        return Commend.objects.filter(question=self).count()

    @property
    def correct_choice(self):
        return Choice.objects.get(question=self, correct_answer=True)

    def add_coin(self):
        if self.currency + 2 <= self.max_currency:
            self.currency += 2
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


class Report(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Commend(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    max_hp = models.IntegerField(default=BASE_HEALTH)
    current_hp = models.IntegerField(default=BASE_HEALTH)
    currency = models.IntegerField(default=0)
    dungeon_currency = models.IntegerField(default=0)
    activity = models.CharField(max_length=100, default="index")
    luck = models.FloatField(default=BASE_LUCK)

    @property
    def player_name(self):
        return self.user.username

    def update_player_stats(self, health: int = 0, dungeon_currency: int = 0, luck: float = 0):
        self.current_hp += health
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

    @property
    def split_log(self):
        return self.log_text.split(';')[:-1]

    def clear_log(self):
        self.log_text = ";;;;;;;;;;"
        self.save()

    def add_log(self, text):
        list_log = self.log_text.split(';')
        del(list_log[0])
        self.log_text = ";".join(list_log)
        self.log_text += f"{text};"
        self.save()

    def __str__(self):
        """Return Log string."""
        return self.log_text

