from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    damage = models.IntegerField(default=1)
    currency = models.IntegerField(default=1)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    enable = models.BooleanField(default=True)

    @property
    def report(self):
        return Report.objects.filter(question=self).count()

    @property
    def commend(self):
        return Commend.objects.filter(question=self).count()

    @property
    def correct_choice(self):
        return Choice.objects.filter(question=self, correct_answer=True)[0]

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
    max_hp = models.IntegerField(default=5)
    current_hp = models.IntegerField(default=5)
    currency = models.IntegerField(default=0)
    dungeon_currency = models.IntegerField(default=0)
    activity = models.CharField(max_length=100, default="index")
    luck = models.FloatField(default=0.2)

    @property
    def player_name(self):
        return self.user.first_name

    def minus_health(self, damage: int):
        self.current_hp -= damage
        self.save()

    def reset_hp(self):
        self.current_hp = self.max_hp
        self.save()

    def earn_currency(self, currency: int):
        self.dungeon_currency += currency
        self.save()

    def clear_dungeon_currency(self):
        self.currency += self.dungeon_currency
        self.dungeon_currency = 0
        self.save()

    def set_luck(self, luck: float = 0.2):
        self.luck = luck
        self.save()

    def set_activity(self, activity: str):
        self.activity = activity
        self.save()

    def dead(self):
        self.set_activity("index")
        self.dungeon_currency = 0
        self.save()


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
        if len(list_log)-1 >= 10:
            del(list_log[0])
            self.log_text = ";".join(list_log)
        self.log_text += f"{text};"
        self.save()

    def __str__(self):
        """Return Log string."""
        return self.log_text

