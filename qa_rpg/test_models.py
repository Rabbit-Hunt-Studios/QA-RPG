from django.test import TestCase
from .models import *
from django.contrib.auth.models import User

empty_log = ['', '', '', '', '', '', '', '', '', '']


class QuestionModelTest(TestCase):

    def setUp(self):
        """Setup for testing Question model."""
        self.system = User.objects.create_user(username="Demo")
        self.system.set_password('12345')
        self.system.save()
        self.question = Question.objects.create(owner=self.system, question_text='test')

    def test_amount_report(self):
        """Report property should return amount of reports the question has."""
        ReportAndCommend.objects.create(user=self.system, question=self.question, vote=0)
        ReportAndCommend.objects.create(user=self.system, question=self.question, vote=0)
        self.assertEqual(self.question.report, 2)

    def test_amount_commend(self):
        """Commend property should return amount of commends the question has."""
        ReportAndCommend.objects.create(user=self.system, question=self.question, vote=1)
        ReportAndCommend.objects.create(user=self.system, question=self.question, vote=1)
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

    def test_reset_player_stats(self):
        """All stats of the player is reset to the default value."""
        self.player.current_hp -= 10
        self.assertEqual(self.player.current_hp, 90)
        self.player.dungeon_currency += 3
        self.player.luck += 0.02
        self.player.reset_stats()
        self.assertEqual(self.player.current_hp, 100)
        self.assertEqual(self.player.max_hp, 100)
        self.assertEqual(self.player.luck, BASE_LUCK)
        self.assertEqual(self.player.dungeon_currency, 0)

    def test_update_player_stats(self):
        """Each value is correctly added to its respective stat."""
        self.player.update_player_stats(health=-20, dungeon_currency=5, luck=0.02)
        self.assertEqual(self.player.current_hp, 80)
        self.assertEqual(self.player.dungeon_currency, 5)
        self.assertEqual(self.player.currency, 0)
        self.assertEqual(self.player.luck, BASE_LUCK + 0.02)

    def test_set_player_activity(self):
        """Player's activity is correctly set."""
        self.assertEqual(self.player.activity, "index")
        self.player.set_activity("dungeon")
        self.assertEqual(self.player.activity, "dungeon")

    def test_dead_player(self):
        """When a player dies, their dungeon currency becomes 0 and returns to index page."""
        self.player.dungeon_currency += 10
        self.assertEqual(self.player.dungeon_currency, 10)
        self.assertEqual(self.player.currency, 0)
        self.player.current_hp -= 200
        self.assertTrue(self.player.check_death())
        self.assertEqual(self.player.dungeon_currency, 0)
        self.assertEqual(self.player.currency, 0)
        self.assertEqual(self.player.activity, "index")

    def test_add_currency_from_dungeon(self):
        """Dungeon currency is added to the player's normal currency."""
        self.player.dungeon_currency += 20
        self.player.add_dungeon_currency()
        self.assertEqual(self.player.dungeon_currency, 0)
        self.assertEqual(self.player.currency, 20)


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
            self.assertEqual(len(self.log.split_log("text")), 10)
        self.assertEqual(self.log.split_log("text"), logs_text[1:])
        self.assertEqual(len(self.log.split_log("text")), 10)

    def test_clear_log(self):
        """clear_log method should empty out the log."""
        self.log.add_log(text='test')
        self.assertEqual(self.log.split_log("text"), ['', '', '', '', '', '', '', '', '', 'test'])
        self.log.clear_log()
        self.assertEqual(self.log.split_log("text"), empty_log)
