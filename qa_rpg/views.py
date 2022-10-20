from django.http import HttpResponseRedirect
from django import views
from django.shortcuts import render
from django.urls import reverse
from .models import Player, Log


def index(request):
    log = Log.objects.get(pk=1)
    log.clear_log()
    log.save()
    return HttpResponseRedirect(reverse('qa_rpg:dungeon'), context={"action": "start"})


class DungeonView(views.generic.DetailView):

    template_name = "qa_rpg/dungeon.html"

    def get(self, request, **kwargs):
        player = Player.objects.get(pk=1)
        try:
            log = Log.objects.get(player=player)
        except Log.DoesNotExist:
            log = Log.object.create(player=player)
        print(kwargs)
        # if kwargs["action"] != "start":
        #     log.add_log("test log")
        log.save()
        return render(request, self.template_name, {"logs": log.split_log})
