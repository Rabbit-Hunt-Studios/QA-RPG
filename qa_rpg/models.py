from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    damage = models.IntegerField(default=1)
    currency = models.IntegerField(default=1)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def report(self):
        return Report.objects.filter(question=self).count()

    def commend(self):
        return Commend.objects.filter(question=self).count()

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

    def reset_hp(self):
        self.current_hp = self.max_hp

    def player_name(self):
        return self.user.first_name


class Log(models.Model):
    log_text = models.CharField(max_length=300, default="")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    @property
    def split_log(self):
        return self.log_text.split(';')[:-1]

    def clear_log(self):
        self.log_text = ""

    def add_log(self, text):
        list_log = self.log_text.split(';')
        if len(list_log)-1 >= 10:
            del(list_log[0])
            self.log_text = ";".join(list_log)
        self.log_text += f"{text};"

    def __str__(self):
        """Return Question string."""
        return self.log_text

