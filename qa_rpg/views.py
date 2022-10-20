from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Question, Choice, Player, Log


class IndexView(generic.TemplateView):

    template_name = 'qa_rpg/index.html'

    def get(self, request):
        return render(request, self.template_name)


class DungeonView(generic.ListView):

    template_name = "qa_rpg/dungeon.html"

    def get(self, request):
        player = Player.objects.get(pk=1)  # dummy player
        try:
            log = Log.objects.get(player=player)
        except Log.DoesNotExist:
            log = Log.object.create(player=player)
            log.save()
        return render(request, self.template_name, {"logs": log.split_log})


def action(request):
    player = Player.objects.get(pk=1)
    try:
        log = Log.objects.get(player=player)
    except Log.DoesNotExist:
        log = Log.object.create(player=player)
    if request.POST['action'] == "walk":
        log.add_log("walk")
    else:
        return redirect("qa_rpg:index")
    log.save()
    return HttpResponseRedirect(reverse("qa_rpg:battle"), headers={"logs": log.split_log})


class BattleView(generic.DetailView):

    template_name = 'battle.html'

    def get(self, request):
        question = Question.objects.get(pk=2)
        return render(request, "qa_rpg/battle.html", {"question": question})


def check(request, question_id):
    question = Question.objects.get(pk=question_id)
    player = Player.objects.get(pk=1)
    log = Log.objects.get(player=player)

    try:
        if request.POST['choice'] == "run away":
            log.add_log("Nigerundayo~~")
            log.save()
            return redirect("qa_rpg:dungeon")
        check_choice = Choice.objects.get(pk=request.POST['choice'])
    except KeyError:
        return render(request, 'qa_rpg/battle.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    if check_choice.correct_answer:
        log.add_log("fought monster, ggez win")
        log.save()
        return redirect("qa_rpg:dungeon")
    else:
        log.add_log("Monster HIT your butt")
        log.save()
        return redirect("qa_rpg:dungeon")


