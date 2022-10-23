from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse
import random
import difflib
from .models import Question, Choice, Player, Log
from .dialogue import *

TREASURE_AMOUNT = [2, 5, 10]
TREASURE_THRESHOLD = 0.5


def get_player_log(player: Player):
    try:
        log = Log.objects.get(player=player)
    except Log.DoesNotExist:
        log = Log.object.create(player=player)
        log.save()
    return log


def check_player_activity(player: Player, activity: list):
    if not difflib.get_close_matches(player.activity, activity):
        if difflib.get_close_matches(player.activity, ["battle"]):
            return f"qa_rpg:{player.activity[:6]}"
        return f"qa_rpg:{player.activity}"
    return None


class IndexView(generic.TemplateView):

    template_name = 'qa_rpg/index.html'

    def get(self, request):
        player = Player.objects.get(pk=1)  # dummy player
        log = get_player_log(player)

        check_url = check_player_activity(player, ["index"])
        if check_url is not None:
            return redirect(check_url)

        player.reset_stats()
        log.clear_log()

        return render(request, self.template_name, {"player": player})


class DungeonView(generic.ListView):

    template_name = "qa_rpg/dungeon.html"

    def get(self, request):
        player = Player.objects.get(pk=1)  # dummy player

        check_url = check_player_activity(player, ["index", "dungeon"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("dungeon")
        log = get_player_log(player)
        return render(request, self.template_name, {"logs": log.split_log, "player": player})


def action(request):

    player = Player.objects.get(pk=1)
    log = get_player_log(player)
    event = random.random()

    if request.POST['action'] == "walk":
        if player.luck >= TREASURE_THRESHOLD and event <= (player.luck-TREASURE_THRESHOLD):
            coins = random.choice(TREASURE_AMOUNT)
            log.add_log(f"You found a treasure chest with {coins} coins in it.")
            player.update_player_stats(dungeon_currency=coins, luck=-(player.luck - TREASURE_THRESHOLD))
        elif event <= player.luck:
            log.add_log(random.choice(MONSTER) + random.choice(BATTLE_DIALOGUE))
            player.set_activity("found monster")
            return redirect("qa_rpg:battle")
        else:
            log.add_log(random.choice(WALK_DIALOGUE))
            player.update_player_stats(luck=0.02)
        return HttpResponseRedirect(reverse("qa_rpg:dungeon"), headers={"logs": log})
    else:
        player.set_activity("index")
        player.add_dungeon_currency()
        return redirect("qa_rpg:index")


class BattleView(generic.DetailView):

    template_name = 'battle.html'

    def get(self, request):
        player = Player.objects.get(pk=1)

        check_url = check_player_activity(player, ["battle", "found monster"])
        if check_url is not None:
            return redirect(check_url)

        if difflib.get_close_matches(player.activity, ["battle"]):
            question_id = int(player.activity[6:])
        else:
            question_id = random.choice(Question.objects.all().values_list("id", flat=True))
        question = Question.objects.get(pk=question_id)

        player.set_activity(f"battle{question_id}")
        return render(request, "qa_rpg/battle.html", {"question": question, "player": player})


def check(request, question_id):

    question = Question.objects.get(pk=question_id)
    player = Player.objects.get(pk=1)
    log = get_player_log(player)

    try:
        if request.POST['choice'] == "run away":
            if random.random() >= player.luck:
                log.add_log(random.choice(RUN_DIALOGUE))
                player.set_activity("dungeon")
                return redirect("qa_rpg:dungeon")
            else:
                run_away = random.choice(RUN_FAIL_DIALOGUE)
                log.add_log(run_away)

                death = check_dead(request, player, question.damage, log)
                if death is not None:
                    return death
                return render(request,
                              'qa_rpg/battle.html',
                              {'question': question,
                               'player': player,
                               'error_message': run_away})

        check_choice = Choice.objects.get(pk=request.POST['choice'])
    except KeyError:
        return render(request, 'qa_rpg/battle.html', {'question': question,
                                                      'player': player,
                                                      'error_message': "You didn't select a choice."})
    if check_choice.correct_answer:
        log.add_log(random.choice(WIN_DIALOGUE))
        log.add_log(f"You earn {question.currency} coins.")
        player.update_player_stats(dungeon_currency=question.currency, luck=0.03)
        player.set_activity("dungeon")
    else:
        log.add_log(random.choice(LOSE_DIALOGUE))
        death = check_dead(request, player, question.damage, log)
        if death is not None:
            return death
        player.set_activity("dungeon")
    return redirect("qa_rpg:dungeon")


def check_dead(request, player: Player, damage: int, log: Log):
    log.add_log(f"You lose {damage} health points.")
    player.update_player_stats(health=-damage)
    if player.current_hp <= 0:
        player.dead()
        return render(request, "qa_rpg/index.html", {'player': player,
                                                     'error_message': "You lost consciousness in the dungeons."})
    return None
