from django.test import TestCase
from .models import *
from django.contrib.auth.models import User
from django.urls import reverse
import random

empty_log = ['', '', '', '', '', '', '', '', '', '']


class IndexViewTest(TestCase):

    def setUp(self):
        """Setup for testing the Index page."""
        self.system = User.objects.create_user(username="demo")
        self.player = Player.objects.create(user=self.system)
        self.log = Log.objects.create(player=self.player)

    def test_get_player_log(self):
        """When a player's log isn't in the database, it automatically creates one."""
        response = self.client.get(reverse("qa_rpg:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.log.split_log, empty_log)
        self.log.delete()
        self.client.get(reverse("qa_rpg:index"))
        log = Log.objects.get(player=self.player)
        self.assertEqual(log.player, self.player)

    def test_not_matching_activity(self):
        """If the player activity is not index, redirect player to the correct page."""
        self.player.set_activity("dungeon")
        response = self.client.get(reverse("qa_rpg:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)
        self.player.set_activity("battle1")
        response = self.client.get(reverse("qa_rpg:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("battle", response.url)


class DungeonViewTest(TestCase):

    def setUp(self):
        """Setup for testing Dungeon page."""
        self.system = User.objects.create_user(username="demo")
        self.player = Player.objects.create(user=self.system)
        self.log = Log.objects.create(player=self.player)

    def test_rendering_dungeon_page(self):
        """Dungeon view should return the player and player's log to html."""
        self.player.set_activity("index")
        response = self.client.get(reverse("qa_rpg:dungeon"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["logs"], empty_log)
        self.assertEqual(response.context["player"], self.player)

    def test_not_matching_activity(self):
        """If the player activity is not dungeon, redirect player to the correct page."""
        self.player.set_activity("battle1")
        response = self.client.get(reverse("qa_rpg:dungeon"))
        self.assertEqual(response.status_code, 302)


class DungeonActionTest(TestCase):

    def setUp(self):
        """Setup for testing actions in dungeon."""
        self.system = User.objects.create_user(username="demo")
        self.system.save()
        self.player = Player.objects.create(user=self.system)
        self.player.set_activity("dungeon")
        self.log = Log.objects.create(player=self.player)
        self.log.save()

    def test_walk_with_no_monster_found(self):
        """When player does not encounter monster, log is updated, player luck is incremented and then redirect to
        dungeon view."""
        random.seed(10)
        response = self.client.post(reverse("qa_rpg:action"), {"action": "walk"})
        self.assertEqual(Player.objects.get(pk=1).luck, 0.26)
        self.assertNotEqual(Log.objects.get(pk=1).split_log[9], "")
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)

    def test_walk_with_monster_found(self):
        """When a player encounters a monster, log is updated, and then redirected to battle view."""
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:action"), {"action": "walk"})
        self.assertNotEqual(Log.objects.get(pk=1).split_log[9], "")
        self.assertEqual(response.status_code, 302)
        self.assertIn("battle", response.url)

    def test_exit_dungeon(self):
        """When player chooses to exit, then redirect to index view."""
        self.player.dungeon_currency = 20
        self.player.save()
        response = self.client.post(reverse("qa_rpg:action"), {"action": "exit"})
        self.assertEqual(response.status_code, 302)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.activity, "index")
        self.assertEqual(self.player.currency, 20)
        self.assertEqual(self.player.dungeon_currency, 0)

    def test_found_treasure(self):
        """When player has high enough luck, they can find treasure."""
        random.seed(123)
        self.player.luck = 0.7
        self.player.save()
        response = self.client.post(reverse("qa_rpg:action"), {"action": "walk"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.luck, 0.55)
        self.assertTrue(self.player.dungeon_currency != 0)


class BattleViewTest(TestCase):

    def setUp(self):
        """Setup for testing battle page."""
        self.system = User.objects.create_user(username="demo")
        self.system.save()
        self.player = Player.objects.create(user=self.system)
        self.player.set_activity("battle1")
        self.question = Question.objects.create(question_text="test", owner=self.system)
        self.question.save()

    def test_rendering_battle_page(self):
        """If player got randomized a monster from dungeon page, randomize a question and render the battle page."""
        self.player.set_activity("found monster")
        response = self.client.get(reverse("qa_rpg:battle"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(pk=1).activity, "battle1")

    def test_already_in_battle(self):
        """If player is already in battle, render the same question."""
        self.player.set_activity("battle1")
        Question.objects.create(question_text="test new question", owner=self.system)
        response = self.client.get(reverse("qa_rpg:battle"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["question"], self.question)

    def test_not_matching_activity(self):
        """If the player activity is not battle, redirect player to the correct page."""
        self.player.set_activity("dungeon")
        response = self.client.get(reverse("qa_rpg:battle"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)
        self.player.set_activity("index")
        response = self.client.get(reverse("qa_rpg:battle"))
        self.assertEqual(response.status_code, 302)


class BattleActionTest(TestCase):

    def setUp(self):
        """Setup for testing actions in battle page."""
        self.system = User.objects.create_user(username="demo")
        self.system.save()
        self.player = Player.objects.create(user=self.system)
        self.player.set_activity("battle1")
        self.question = Question.objects.create(question_text="test", owner=self.system)
        self.question.save()
        self.correct = Choice.objects.create(question=self.question, choice_text='yes', correct_answer=True)
        self.correct.save()
        self.wrong = Choice.objects.create(question=self.question, choice_text='no', correct_answer=False)
        self.wrong.save()

    def test_player_answers_correctly(self):
        """When player chooses the correct answer, player is given currency and health is not deducted."""
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": self.correct.id})
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.current_hp, self.player.max_hp)
        self.assertEqual(self.player.dungeon_currency, self.question.currency)
        self.assertEqual(self.player.luck, BASE_LUCK + 0.03)
        self.assertEqual(self.player.activity, "dungeon")

    def test_player_answers_incorrectly(self):
        """When player chooses the incorrect answer, player health is deducted."""
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": self.wrong.id})
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.current_hp, self.player.max_hp - self.question.damage)
        self.assertEqual(self.player.dungeon_currency, 0)
        self.assertEqual(self.player.luck, BASE_LUCK)
        self.assertEqual(self.player.activity, "dungeon")

    def test_player_dies_to_question_damage(self):
        """If player answers incorrectly, dungeon currency becomes zero and return to index."""
        self.player.current_hp = 10
        self.player.save()
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": self.wrong.id})
        self.assertEqual(response.status_code, 200)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.currency, 0)
        self.assertEqual(self.player.activity, "index")

    def test_player_runs_away_successfully(self):
        """When player chooses run away and randoms high enough float, return to dungeon page."""
        random.seed(10)
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": "run away"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)
        self.assertEqual(Player.objects.get(pk=1).activity, "dungeon")

    def test_player_does_not_run_away_successfully(self):
        """When player chooses run away and randoms low float, stay in battle page and deduct health."""
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": "run away"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(pk=1).activity, "battle1")

    def test_player_dies_to_unsuccessful_run_away(self):
        """If player chooses run away and randoms low float and health falls below zero, dungeon currency becomes
        zero and return to index."""
        self.player.current_hp = 10
        self.player.save()
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": "run away"})
        self.assertEqual(response.status_code, 200)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.currency, 0)
        self.assertEqual(self.player.activity, "index")