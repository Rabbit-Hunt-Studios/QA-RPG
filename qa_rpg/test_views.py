from django.test import TestCase
from .models import *
from django.contrib.auth.models import User
from django.urls import reverse
import random

empty_log = ['', '', '', '', '', '', '', '', '', '']


class IndexViewTest(TestCase):

    def setUp(self):
        """Setup for testing the Index page."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username=self.user, password="12345")
        self.player = Player.objects.create(user=self.user)
        self.log = Log.objects.create(player=self.player)

    def test_get_player_log(self):
        """When a player's log isn't in the database, it automatically creates one."""
        response = self.client.get(reverse("qa_rpg:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.log.split_log("text"), empty_log)
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
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username=self.user, password="12345")
        self.player = Player.objects.create(user=self.user)
        self.log = Log.objects.create(player=self.player)

    def test_rendering_dungeon_page(self):
        """Dungeon view should return the player and player's log to html."""
        self.player.set_activity("select")
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
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("dungeon")
        self.log = Log.objects.create(player=self.player)
        self.log.save()

    def test_walk_with_no_monster_found(self):
        """When player does not encounter monster, log is updated, player luck is incremented and then redirect to
        dungeon view."""
        random.seed(10)
        response = self.client.post(
            reverse("qa_rpg:action"), {"action": "walk"})
        self.assertEqual(Player.objects.get(pk=1).luck, 0.27)
        self.assertNotEqual(Log.objects.get(pk=1).split_log("text")[9], "")
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)

    def test_walk_with_monster_found(self):
        """When a player encounters a monster, log is updated, and then redirected to battle view."""
        random.seed(100)
        response = self.client.post(
            reverse("qa_rpg:action"), {"action": "walk"})
        self.assertNotEqual(Log.objects.get(pk=1).split_log("text")[9], "")
        self.assertEqual(response.status_code, 302)
        self.assertIn("battle", response.url)

    def test_exit_dungeon(self):
        """When player chooses to exit, then redirect to index view."""
        self.player.dungeon_currency = 20
        self.player.save()
        response = self.client.post(
            reverse("qa_rpg:action"), {"action": "exit"})
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
        response = self.client.post(
            reverse("qa_rpg:action"), {"action": "walk"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.luck, 0.5)


class BattleViewTest(TestCase):

    def setUp(self):
        """Setup for testing battle page."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.system = User.objects.create_user(username="test")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("battle1")
        self.question = Question.objects.create(
            question_text="test", owner=self.system)
        self.question.save()

    def test_rendering_battle_page(self):
        """If player got randomized a monster from dungeon page, randomize a question and render the battle page."""
        self.player.set_activity("found monster")
        response = self.client.get(reverse("qa_rpg:battle"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(
            user=self.user).activity, "battle1")

    def test_already_in_battle(self):
        """If player is already in battle, render the same question."""
        self.player.set_activity("battle1")
        Question.objects.create(
            question_text="test new question", owner=self.system)
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
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.system = User.objects.create_user(username="test")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("battle1")
        self.question = Question.objects.create(
            question_text="test", owner=self.system)
        self.question.save()
        self.correct = Choice.objects.create(
            question=self.question, choice_text='yes', correct_answer=True)
        self.correct.save()
        self.wrong = Choice.objects.create(
            question=self.question, choice_text='no', correct_answer=False)
        self.wrong.save()

    def test_player_answers_correctly(self):
        """When player chooses the correct answer, player is given currency and health is not deducted."""
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": self.correct.id, "option": "not select"})
        self.player = Player.objects.get(pk=1)
        self.question = Question.objects.get(pk=1)
        self.assertEqual(self.player.current_hp, self.player.max_hp)
        self.assertEqual(self.player.dungeon_currency, 1)
        self.assertEqual(self.question.currency, 0)
        self.assertEqual(self.player.luck, BASE_LUCK + 0.04)
        self.assertEqual(self.player.activity, "dungeon")

    def test_player_answers_incorrectly(self):
        """When player chooses the incorrect answer, player health is deducted."""
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": self.wrong.id, "option": "not select"})
        self.player = Player.objects.get(pk=1)
        self.question = Question.objects.get(pk=1)
        self.assertEqual(self.player.current_hp,
                         self.player.max_hp - self.question.damage)
        self.assertEqual(self.question.currency, 5)
        self.assertEqual(self.player.dungeon_currency, 0)
        self.assertEqual(self.player.luck, BASE_LUCK)
        self.assertEqual(self.player.activity, "dungeon")

    def test_player_dies_to_question_damage(self):
        """If player answers incorrectly, dungeon currency becomes zero and return to index."""
        self.player.current_hp = 10
        self.player.save()
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),
                                    {"choice": self.wrong.id, "option": "not select"})
        self.assertEqual(response.status_code, 200)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.currency, 0)
        self.assertEqual(self.player.activity, "index")

    def test_player_runs_away_successfully(self):
        """When player chooses run away and randoms high enough float, return to dungeon page."""
        random.seed(10)
        response = self.client.post(reverse("qa_rpg:run_away", args=(
            self.question.id,)), {"option": "not select"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("dungeon", response.url)
        self.assertEqual(Player.objects.get(pk=1).activity, "dungeon")

    def test_player_does_not_run_away_successfully(self):
        """When player chooses run away and randoms low float, stay in battle page and deduct health."""
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:run_away", args=(
            self.question.id,)), {"option": "not select"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(pk=1).activity, "battle1")

    def test_player_dies_to_unsuccessful_run_away(self):
        """If player chooses run away and randoms low float and health falls below zero, dungeon currency becomes
        zero and return to index."""
        self.player.current_hp = 10
        self.player.save()
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:run_away", args=(
            self.question.id,)), {"option": "not select"})
        self.assertEqual(response.status_code, 200)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.currency, 0)
        self.assertEqual(self.player.activity, "index")


class SummonViewTest(TestCase):

    def setUp(self):
        """Setup for testing summon view page."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.system = User.objects.create_user(username="test")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("summon4")

    def test_rendering_summon_page(self):
        """Test that player actually in summon page"""
        self.player.set_activity("choose1")
        response = self.client.get(reverse("qa_rpg:summon"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(
            user=self.user).activity, "summon4 1")

    def test_rendering_summon_page_from_another_page(self):
        self.player.set_activity("battle")
        response = self.client.get(reverse("qa_rpg:summon"))
        self.assertEqual(response.status_code, 302)


class CreateQuestionTest(TestCase):
    """Testing actions in summon page."""

    def setUp(self):
        """Setup for testing actions in summon page."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.system = User.objects.create_user(username="test")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("summon4")
        self.inventory = Inventory.objects.create(player=self.player)
        self.inventory.update_templates({0: 2})

    def test_remain_currency_after_summon(self):
        """Test remain currency after summoning."""
        self.player.set_activity("summon4 1")
        self.player = Player.objects.get(pk=1)
        self.player.currency = 200
        self.player.save()
        response = self.client.post(reverse("qa_rpg:create"),
                                    {"question0": "What ",
                                     "question1": "is ",
                                     "question2": "this",
                                     "question3": "?",
                                     "choice0": "1",
                                     "choice1": "2",
                                     "choice2": "3",
                                     "choice3": "4",
                                     "fee": "150", "index": "0", "template_id": "0"})
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.currency, 50)

    def test_player_not_fill_every_field(self):
        """Test player not fill all field in create question."""
        self.player.set_activity("summon4 1")
        self.player = Player.objects.get(pk=1)
        self.player.currency = 200
        self.player.save()
        response = self.client.post(reverse("qa_rpg:create"),
                                    {"question0": "What ",
                                     "question1": "is ",
                                     "question2": "this",
                                     "question3": "?",
                                     "choice1": "2",
                                     "choice2": "3",
                                     "choice3": "4",
                                     "fee": "150", "index": "0", "template_id": "0"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.player.currency, 200)

    def test_player_not_have_enough_coin(self):
        """Test player not have enough coin for create question."""
        self.player = Player.objects.get(pk=1)
        self.player.currency = 20
        self.player.save()
        response = self.client.post(reverse("qa_rpg:create"),
                                    {"question0": "What ",
                                     "question1": "is ",
                                     "question2": "this",
                                     "question3": "?",
                                     "choice0": "1",
                                     "choice1": "2",
                                     "choice2": "3",
                                     "choice3": "4",
                                     "fee": "150", "index": "0", "template_id": "0"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.player.currency, 20)


class ProfileViewTest(TestCase):
    """Testing actions in profile page."""

    def setUp(self):
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.system = User.objects.create_user(username="test")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("profile")
        self.player.currency = 0
        self.question = Question.objects.create(
            question_text="test", owner=self.system, pk=1)
        self.question.currency = 10
        self.question.save()

    def test_rendering_profile_page(self):
        """Test that player actually in summon page"""
        response = self.client.get(reverse("qa_rpg:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(
            user=self.user).activity, "profile")

    def test_rendering_profile_page_from_another_page(self):
        self.player.set_activity("index")
        response = self.client.get(reverse("qa_rpg:profile"))
        self.assertEqual(response.status_code, 200)

    def test_rendering_profile_page_not_in_check_url(self):
        self.player.set_activity("battle")
        response = self.client.get(reverse("qa_rpg:profile"))
        self.assertEqual(response.status_code, 302)

    def test_claim_coin(self):
        random.seed(100)
        respond = self.client.post(
            reverse("qa_rpg:claim", args=(self.question.id,)))
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.currency, 10)


class TreasureViewTest(TestCase):

    def setUp(self):
        """Setup user for the treasure page."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.system = User.objects.create_user(username="test")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("dungeon")

    def test_rendering_treasure_page(self):
        """Test that player in treasure page."""
        self.player.set_activity("treasure")
        response = self.client.get(reverse("qa_rpg:treasure"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.get(
            user=self.user).activity, "treasure")


class TreasureActionTest(TestCase):

    def setUp(self):
        """Setup for testing actions in treasure page."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.client.login(username="demo", password="12345")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("treasure")

    def test_claim_coin_after_pick_up_treasure(self):
        """Test that after pick up a treasure,the player gains bonus coins."""
        random.seed(10)
        self.player.dungeon_currency = 10
        self.player.luck = 0.75
        self.player.save()
        response = self.client.post(
            reverse("qa_rpg:treasure_action"), {"action": "pick up"})
        self.assertEqual(response.status_code, 302)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.activity, "dungeon")
        self.assertEqual(self.player.current_hp, self.player.max_hp)
        self.assertNotEqual(self.player.dungeon_currency, 10)

    def test_lose_health_after_pick_up_treasure(self):
        """Test that after pick up a treasure, the player loses health."""
        random.seed(150)
        self.player.dungeon_currency = 20
        self.player.luck = 0.25
        self.player.save()
        response = self.client.post(
            reverse("qa_rpg:treasure_action"), {"action": "pick up"})
        self.assertEqual(response.status_code, 302)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.activity, "dungeon")
        self.assertEqual(self.player.dungeon_currency, 20)
        self.assertNotEqual(self.player.current_hp, self.player.max_hp)

    def test_run_away_from_treasure(self):
        """Test that user return to dungeon page after run away from treasure."""
        random.seed(100)
        self.player.dungeon_currency = 20
        self.player.current_hp = 75
        self.player.save()
        response = self.client.post(
            reverse("qa_rpg:treasure_action"), {"action": "run away"})
        self.assertEqual(response.status_code, 302)
        self.player = Player.objects.get(pk=1)
        self.assertEqual(self.player.activity, "dungeon")
        self.assertEqual(self.player.dungeon_currency, 20)
        self.assertEqual(self.player.current_hp, 75)


class ReportandCommendTest(TestCase):

    def setUp(self):
        """Setup user for testing report and commend."""
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.user2 = User.objects.create_user(username="admin")
        self.user2.save()
        self.client.login(username="demo", password="12345")
        self.player = Player.objects.create(user=self.user)
        self.player.set_activity("battle1")
        self.player.save()
        self.question = Question.objects.create(question_text="test", owner=self.user, pk=1)
        self.question.save()
        self.correct = Choice.objects.create(
            question=self.question, choice_text='yes', correct_answer=True)
        self.correct.save()
        self.wrong = Choice.objects.create(
            question=self.question, choice_text='no', correct_answer=False)
        self.wrong.save()


    def test_one_report_commend_per_user(self):
        """Test that user can only report or commend 1 time for each question."""
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),  {"choice": self.correct.id, "option": "report"})
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)),  {"choice": self.correct.id, "option": "commend"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReportAndCommend.objects.filter(question=self.question).count(), 1)

    def test_deactivate_question(self):
        """Test that after the report exceed the limit, the question will be disabled."""
        random.seed(100)
        response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)), {"choice": self.correct.id, "option": "report"})
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        for i in range(1, 8):
            self.user = User.objects.create_user(username=f"test{i}")
            self.user.set_password(f"Testing{i}")
            self.user.save()
            self.client.login(username=f"Test{i}", password=f"Testing{i}")
            self.player = Player.objects.create(user=self.user)
            self.player.set_activity("battle1")
            self.player.save()
            response = self.client.post(reverse("qa_rpg:check", args=(self.question.id,)), {"choice": self.correct.id, "option": "report"})
            self.client.logout()
        self.question = Question.objects.get(pk=self.question.id,)
        self.report_commends = ReportAndCommend.objects.filter(question=self.question).count()
        self.assertEqual(self.report_commends, 8)
        self.assertEqual(self.question.enable, False)


        