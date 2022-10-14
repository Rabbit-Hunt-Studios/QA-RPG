from django.test import TestCase
from .models import *
from django.contrib.auth.models import User
from .views import *


class QuestionModelTest(TestCase):

    def setUp(self):
        """Setup for testing Question model."""
        self.system = User.objects.create_user(username="Demo")
        self.system.set_password('12345')
        self.system.save()
        self.question = Question.objects.create(owner=self.system, question_text='test')

    def test_amount_report(self):
        """Report property should return amount of reports the question has."""
        Report.objects.create(user=self.system, question=self.question)
        Report.objects.create(user=self.system, question=self.question)
        self.assertEqual(self.question.report, 2)

    def test_amount_commend(self):
        """Commend property should return amount of commends the question has."""
        Commend.objects.create(user=self.system, question=self.question)
        Commend.objects.create(user=self.system, question=self.question)
        self.assertEqual(self.question.commend, 2)

    def test_get_correct_answer(self):
        """correct_choice property returns the right answer."""
        choice = Choice.objects.create(question=self.question, choice_text='yes', correct_answer=True)
        Choice.objects.create(question=self.question, choice_text='no', correct_answer=False)
        self.assertEqual(self.question.correct_choice, choice)


class PlayerModelTest(TestCase):

    def setUp(self):
        """Setup for testing Question model."""
        self.system = User.objects.create_user(username="Demo")
        self.system.set_password('12345')
        self.system.save()
        self.question = Question.objects.create(owner=self.system, question_text='test')
        self.player = Player.objects.create(user=self.system)

    def test_reset_health(self):
        """Health of the player is reset to the maximum health."""
        self.player.current_hp -= 2
        self.assertEqual(self.player.current_hp, 3)
        self.player.reset_hp()
        self.assertEqual(self.player.current_hp, 5)
        self.assertEqual(self.player.max_hp, 5)


class LogModelTest(TestCase):

    def setUp(self):
        """Setup for testing Question model."""
        self.system = User.objects.create_user(username="Demo")
        self.system.set_password('12345')
        self.system.save()
        self.question = Question.objects.create(owner=self.system, question_text='test')
        self.player = Player.objects.create(user=self.system)
        self.log = Log.objects.create(player=self.player)

    def test_add_more_than_10_logs(self):
        """If logs exceed 10, the first one is deleted and the new log is added in the back."""
        logs_text = ['Entering dungeon',
                     'Walking forward',
                     'Found a monster',
                     'Battling with monster',
                     'Killed the monster',
                     'Earned currency',
                     'Nothing happen',
                     'Walking forward',
                     'Walking forward',
                     'Nothing happen',
                     'Exiting dungeon']
        for text in logs_text:
            self.log.add_log(text=text)
        self.assertEqual(self.log.split_log, logs_text[1:])
        self.assertEqual(len(self.log.split_log), 10)

    def test_clear_log(self):
        """clear_log method should empty out the log."""
        self.log.add_log(text='test')
        self.assertEqual(self.log.split_log, ['test'])
        self.log.clear_log()
        self.assertEqual(self.log.split_log, [])
