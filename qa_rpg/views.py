from django.utils.decorators import method_decorator
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import random
import difflib

from django.views.decorators.cache import never_cache

from .models import Question, Choice, Player, Log, Inventory
from .dialogue import Dialogue
from .template_question import TemplateCatalog

TREASURE_AMOUNT = [1, 5, 10, 15, 30, 35, 40, 45, 50, 60, 69, 70, 77]
TREASURE_THRESHOLD = 0.5
CATEGORY = ['General Knowledge', 'Entertainment', 'Science', 'Math',
            'History', 'Technology', 'Sport']


def get_player(user: User):
    while True:
        try:
            player = Player.objects.get(user=user)
            log = Log.objects.get(player=player)
            inventory = Inventory.objects.get(player=player)
            break
        except Player.DoesNotExist:
            player = Player.objects.create(user=user)
            player.save()
            continue
        except Log.DoesNotExist:
            log = Log.objects.create(player=player)
            log.save()
            continue
        except Inventory.DoesNotExist:
            inventory = Inventory.objects.create(player=player)
            inventory.save()
            continue
    return player, log, inventory


def check_player_activity(player: Player, activity: list):
    if not difflib.get_close_matches(player.activity, activity):
        if difflib.get_close_matches(player.activity, ["battle", "summon"]):
            return f"qa_rpg:{player.activity[:6]}"
        return f"qa_rpg:{player.activity}"
    return None


class HomeView(generic.TemplateView):

    template_name = 'qa_rpg/homepage.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        return render(request, self.template_name)


class IndexView(LoginRequiredMixin, generic.TemplateView):

    template_name = 'qa_rpg/index.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["summon", "index", "profile"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("index")
        player.reset_stats()
        log.clear_log()
        log.clear_question()
        player.set_activity("index")
        return render(request, self.template_name, {"player": player})


class DungeonView(LoginRequiredMixin, generic.ListView):

    template_name = "qa_rpg/dungeon.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["index", "dungeon"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("dungeon")
        return render(request, self.template_name, {"logs": log.split_log("text"), "player": player})


@never_cache
def action(request):

    player, log, inventory = get_player(request.user)
    event = random.random()

    if request.POST['action'] == "walk":
        url = "qa_rpg:dungeon"
        if player.luck >= TREASURE_THRESHOLD and event <= (player.luck-TREASURE_THRESHOLD):
            log.add_log(f"You found a treasure chest")
            player.update_player_stats(luck=-(player.luck - TREASURE_THRESHOLD))
            url = "qa_rpg:treasure"
        elif event <= player.luck:
            log.add_log(Dialogue.MONSTER.get_text + Dialogue.BATTLE_DIALOGUE.get_text)
            player.set_activity("found monster")
            url = "qa_rpg:battle"
        else:
            log.add_log(Dialogue.WALK_DIALOGUE.get_text)
            player.update_player_stats(luck=0.02)
        return redirect(url)
    else:
        player.set_activity("index")
        player.add_dungeon_currency()
        return redirect("qa_rpg:index")


class TreasureView(LoginRequiredMixin, generic.DetailView):

    template_name = "qa_rpg/treasure.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["dungeon", "treasure"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity(f"treasure")
        return render(request, self.template_name, {"player": player})


@never_cache
def treasure_action(request):
    player, log, inventory = get_player(request.user)
    event = random.random()

    if request.POST['action'] == "pick up":
        if player.luck >= event:
            coins = random.choice(TREASURE_AMOUNT)
            log.add_log(f"You found {coins} coins in treasure chest.")
            player.update_player_stats(dungeon_currency=coins)
        else:
            log.add_log("Oh No!! Mimic chest bite your leg")
            damages = random.randint(1, 10)
            player.update_player_stats(health=-damages)
            if player.check_death():
                messages.error(request, "You lost consciousness in the dungeons.")
                return render(request, "qa_rpg/index.html", {'player': player})

            log.add_log(f"You lose {damages} health points.")
    else:
        log.add_log(f"You walk away from treasure chest.")

    player.set_activity("dungeon")
    return redirect("qa_rpg:dungeon")


class BattleView(LoginRequiredMixin, generic.DetailView):

    template_name = 'battle.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)
        admin = User.objects.get(pk=2)

        check_url = check_player_activity(player, ["battle", "found monster"])
        if check_url is not None:
            return redirect(check_url)

        if difflib.get_close_matches(player.activity, ["battle"]):
            question_id = int(player.activity[6:])
        else:
            if len(log.split_log("question")) != 10:
                question_id = random.choice(Question.objects.filter(~Q(owner=request.user))
                                            .values_list("id", flat=True))
                if Question.objects.get(pk=question_id).owner == admin:
                    log.add_question(question_id)
                else:
                    log.clear_question()
            else:
                question_id = random.choice(Question.objects.filter(~Q(owner=request.user), ~Q(owner=admin))
                                            .values_list("id", flat=True))
                log.clear_question()
        question = Question.objects.get(pk=question_id)

        player.set_activity(f"battle{question_id}")
        return render(request, "qa_rpg/battle.html", {"question": question, "player": player})


@never_cache
def check(request, question_id):

    question = Question.objects.get(pk=question_id)
    player, log, inventory = get_player(request.user)

    try:
        if request.POST['choice'] == "run away":
            if random.random() >= player.luck:
                log.add_log(Dialogue.RUN_DIALOGUE.get_text)
                player.set_activity("dungeon")
                return redirect("qa_rpg:dungeon")
            else:
                run_fail = Dialogue.RUN_FAIL_DIALOGUE.get_text
                log.add_log(run_fail)

                player.update_player_stats(health=-question.damage)
                question.add_coin()
                if player.check_death():
                    messages.error(request, "You lost consciousness in the dungeons.")
                    return render(request, "qa_rpg/index.html", {'player': player})

                messages.error(request, run_fail)
                return render(request,
                              'qa_rpg/battle.html',
                              {'question': question,
                               'player': player})

        check_choice = Choice.objects.get(pk=request.POST['choice'])

        if check_choice.correct_answer:
            log.add_log(Dialogue.WIN_DIALOGUE.get_text)
            earn_coins = get_coins(question.damage)
            log.add_log(f"You earn {earn_coins} coins.")
            player.update_player_stats(dungeon_currency=earn_coins, luck=0.04)
            player.set_activity("dungeon")
        else:
            log.add_log(Dialogue.LOSE_DIALOGUE.get_text)
            player.update_player_stats(health=-question.damage)
            question.add_coin()
            if player.check_death():
                messages.error(request, "You lost consciousness in the dungeons.")
                return render(request, "qa_rpg/index.html", {'player': player})

            log.add_log(f"You lose {question.damage} health points.")
            player.set_activity("dungeon")

        return redirect("qa_rpg:dungeon")

    except KeyError:
        messages.error(request, "You didn't select a attack move.")
        return redirect("qa_rpg:battle")


def get_coins(damage: int):
    for i in range(2, 6):
        if i * 10 <= damage < (i + 1) * 10:
            return random.randrange(start=i*8, stop=(i + 1)*8, step=1)
    return 50


class TemplateChooseView(LoginRequiredMixin, generic.DetailView):

    template_name = "qa_rpg/template_choose.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["summon", "index"])
        if check_url is not None:
            return redirect(check_url)

        available = {}
        for index in inventory.get_templates().keys():
            available["+ ".join(TemplateCatalog.TEMPLATES.get_template(index))] = index

        return render(request, self.template_name, {"selection": available})


@never_cache
def choose(request):
    player, log, inventory = get_player(request.user)
    player.set_activity(f"choose{request.GET['index']}")
    return redirect("qa_rpg:summon")


class SummonView(LoginRequiredMixin, generic.DetailView):

    template_name = "summon.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["choose", "summon"])
        if check_url is not None:
            return redirect(check_url)

        template_index = int(player.activity[6:])
        player.set_activity("summon4")
        return render(request, "qa_rpg/summon.html",
                      {"question": TemplateCatalog.TEMPLATES.get_template(template_index),
                       "amount": range(4),
                       "fee": TemplateCatalog.TEMPLATES.get_price(template_index),
                       "category": CATEGORY, "player": player})


@never_cache
def create(request):
    player, log, inventory = get_player(request.user)

    try:
        question_text = ''
        for i in range(4):
            question_text += request.POST[f'question{i}']
        question_text += "?"
        choices = {}
        correct_index = int(request.POST['index'])
        for num in range(int(player.activity[6:])):
            if num == correct_index:
                choices[request.POST[f'choice{num}']] = True
            else:
                choices[request.POST[f'choice{num}']] = False
    except KeyError:
        messages.error(request, "Please fill in every field and select a correct answer.")
        return redirect("qa_rpg:summon")

    summon_fee = int(request.POST['fee'])
    if summon_fee > player.currency:
        messages.error(request, "You don't have enough coins to summon a monster.")
        return redirect("qa_rpg:summon")

    question = Question.objects.create(question_text=question_text,
                                       owner=request.user, category="player")
    question.save()
    for choice_text in choices.keys():
        choice = Choice.objects.create(choice_text=choice_text,
                                       correct_answer=choices[choice_text],
                                       question=question)
        choice.save()
    player.set_activity("index")
    messages.error(request, "Successfully summoned a new monster.")
    player.currency -= summon_fee
    player.save()
    return redirect('qa_rpg:index')


class ProfileView(LoginRequiredMixin, generic.TemplateView):

    template_name = 'qa_rpg/profile.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)
        questions = Question.objects.filter(owner=player.user)

        check_url = check_player_activity(player, ["index", "profile"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("profile")

        return render(request, self.template_name, {"player": player, "questions": questions})


@never_cache
def claim_coin(request, question_id):
    player, log, inventory = get_player(request.user)
    questions = Question.objects.get(pk=question_id)

    player.currency += questions.currency
    questions.currency = 0
    player.save()
    questions.save()
    return redirect('qa_rpg:profile')

