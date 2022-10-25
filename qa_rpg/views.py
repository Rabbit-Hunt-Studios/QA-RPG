from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
import random
import difflib
from .models import Question, Choice, Player, Log
from .dialogue import Dialogue

TREASURE_AMOUNT = [1, 5, 10, 15, 30]
TREASURE_THRESHOLD = 0.55


def get_player_log(player: Player):
    try:
        log = Log.objects.get(player=player)
    except Log.DoesNotExist:
        log = Log.objects.create(player=player)
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

    player = Player.objects.get(pk=1)  # dummy player
    log = get_player_log(player)
    event = random.random()

    if request.POST['action'] == "walk":
        url = "qa_rpg:dungeon"
        if player.luck >= TREASURE_THRESHOLD and event <= (player.luck-TREASURE_THRESHOLD):
            coins = random.choice(TREASURE_AMOUNT)
            log.add_log(f"You found a treasure chest with {coins} coins in it.")
            player.update_player_stats(dungeon_currency=coins, luck=-(player.luck - TREASURE_THRESHOLD))
        elif event <= player.luck:
            log.add_log(Dialogue.MONSTER.get_text + Dialogue.BATTLE_DIALOGUE.get_text)
            player.set_activity("found monster")
            url = "qa_rpg:battle"
        else:
            log.add_log(Dialogue.WALK_DIALOGUE.get_text)
            player.update_player_stats(luck=0.01)
        return redirect(url)
    else:
        player.set_activity("index")
        player.add_dungeon_currency()
        return redirect("qa_rpg:index")


class BattleView(generic.DetailView):

    template_name = 'battle.html'

    def get(self, request):
        player = Player.objects.get(pk=1)  # dummy player

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
    player = Player.objects.get(pk=1)  # dummy player
    log = get_player_log(player)

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
            log.add_log(f"You earn {question.currency} coins.")
            player.update_player_stats(dungeon_currency=question.currency, luck=0.03)
            player.set_activity("dungeon")
        else:
            log.add_log(Dialogue.LOSE_DIALOGUE.get_text)
            player.update_player_stats(health=-question.damage)
            if player.check_death():
                messages.error(request, "You lost consciousness in the dungeons.")
                return render(request, "qa_rpg/index.html", {'player': player})

            log.add_log(f"You lose {question.damage} health points.")
            player.set_activity("dungeon")

        return redirect("qa_rpg:dungeon")

    except KeyError:
        messages.error(request, "You didn't select a attack move.")
        return redirect("qa_rpg:battle")
