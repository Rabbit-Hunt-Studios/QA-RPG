from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse
import random
from .models import Question, Choice, Player, Log

TREASURE_AMOUNT = [1, 5, 10]
TREASURE_THRESHOLD = 0.5


def get_player_log(player: Player):
    try:
        log = Log.objects.get(player=player)
    except Log.DoesNotExist:
        log = Log.object.create(player=player)
        log.save()
    return log


def check_player_activity(player: Player, activity: list):
    if player.activity not in activity:
        return True
    return False


class IndexView(generic.TemplateView):
    template_name = 'qa_rpg/index.html'

    def get(self, request):
        player = Player.objects.get(pk=1)
        log = get_player_log(player)

        if check_player_activity(player, ["index"]):
            return redirect(f"qa_rpg:{player.activity}")

        player.reset_hp()
        player.set_luck()
        player.clear_dungeon_currency()
        log.clear_log()

        return render(request, self.template_name, {"player": player})


class DungeonView(generic.ListView):
    template_name = "qa_rpg/dungeon.html"

    def get(self, request):
        player = Player.objects.get(pk=1)  # dummy player
        if check_player_activity(player, ["index", "dungeon"]):
            return redirect(f"qa_rpg:{player.activity}")
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
            player.earn_currency(coins)
            player.set_luck(TREASURE_THRESHOLD)
        elif event <= player.luck:
            log.add_log("Monster want to hit you")
            return redirect("qa_rpg:battle")
        else:
            log.add_log("Walk")
            player.set_luck(player.luck + 0.02)
        return HttpResponseRedirect(reverse("qa_rpg:dungeon"), headers={"logs": log})
    else:
        player.set_activity("index")
        return redirect("qa_rpg:index")


class BattleView(generic.DetailView):
    template_name = 'battle.html'

    def get(self, request):
        question_id = random.choice(Question.objects.all().values_list("id", flat=True))
        question = Question.objects.get(pk=question_id)
        player = Player.objects.get(pk=1)
        if check_player_activity(player, ["dungeon", "battle"]):
            return redirect(f"qa_rpg:{player.activity}")
        player.set_activity("battle")
        return render(request, "qa_rpg/battle.html", {"question": question, "player": player})


def check(request, question_id):
    question = Question.objects.get(pk=question_id)
    player = Player.objects.get(pk=1)
    log = get_player_log(player)

    try:
        if request.POST['choice'] == "run away":
            log.add_log("Nigerundayo~~")
            player.set_activity("dungeon")
            return redirect("qa_rpg:dungeon")
        check_choice = Choice.objects.get(pk=request.POST['choice'])
    except KeyError:
        return render(request, 'qa_rpg/battle.html', {
            'question': question,
            'player': player,
            'error_message': "You didn't select a choice.",
        })
    if check_choice.correct_answer:
        log.add_log("fought monster, ggez win")
        log.add_log(f"you earn {question.currency} coins")
        player.earn_currency(question.currency)
        player.set_luck(player.luck+0.05)
        player.set_activity("dungeon")
        return redirect("qa_rpg:dungeon")
    else:
        log.add_log("Monster HIT your butt")
        player.hit(question.damage)
        if player.current_hp <= 0:
            player.dead()
            return render(request, "qa_rpg/index.html", {'player': player,
                                                         'error_message': "You die.",})
        player.set_activity("dungeon")
        return redirect("qa_rpg:dungeon")
