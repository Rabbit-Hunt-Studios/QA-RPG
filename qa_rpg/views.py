from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse
import random
from .models import Question, Choice, Player, Log


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
        log.clear_log()

        print(request.get_full_path())
        return render(request, self.template_name)


class DungeonView(generic.ListView):
    template_name = "qa_rpg/dungeon.html"

    def get(self, request):
        player = Player.objects.get(pk=1)  # dummy player
        print(player.activity)
        if check_player_activity(player, ["index", "dungeon"]):
            return redirect(f"qa_rpg:{player.activity}")
        player.set_activity("dungeon")
        log = get_player_log(player)
        return render(request, self.template_name, {"logs": log.split_log})


def action(request):
    player = Player.objects.get(pk=1)
    log = get_player_log(player)
    if request.POST['action'] == "walk":
        log.add_log("walk")
    else:
        player.set_activity("index")
        return redirect("qa_rpg:index")
    return HttpResponseRedirect(reverse("qa_rpg:battle"), headers={"logs": log.split_log})


class BattleView(generic.DetailView):
    template_name = 'battle.html'

    def get(self, request):
        question = Question.objects.get(pk=1)
        player = Player.objects.get(pk=1)
        if check_player_activity(player, ["dungeon", "battle"]):
            return redirect(f"qa_rpg:{player.activity}")
        player.set_activity("battle")
        return render(request, "qa_rpg/battle.html", {"question": question})


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
            'error_message': "You didn't select a choice.",
        })
    if check_choice.correct_answer:
        log.add_log("fought monster, ggez win")
        player.set_activity("dungeon")
        return redirect("qa_rpg:dungeon")
    else:
        log.add_log("Monster HIT your butt")
        player.set_activity("dungeon")
        return redirect("qa_rpg:dungeon")
