from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
import random
import difflib
from .models import Question, Choice, Player, Log
from .dialogue import Dialogue

TREASURE_AMOUNT = [5, 10, 15, 30, 35]
TREASURE_THRESHOLD = 0.55
CATEGORY = ['General Knowledge', 'Entertainment', 'Science', 'Math',
            'History', 'Technology', 'Sport']


def get_player_log(player: Player):
    try:
        log = Log.objects.get(player=player)
    except Log.DoesNotExist:
        log = Log.objects.create(player=player)
        log.save()
    return log


def check_player_activity(player: Player, activity: list):
    if not difflib.get_close_matches(player.activity, activity):
        if difflib.get_close_matches(player.activity, ["battle", "summon"]):
            return f"qa_rpg:{player.activity[:6]}"
        return f"qa_rpg:{player.activity}"
    return None


class IndexView(LoginRequiredMixin, generic.TemplateView):

    template_name = 'qa_rpg/index.html'

    def get(self, request):
        player = Player.objects.get(user=request.user)
        log = get_player_log(player)

        check_url = check_player_activity(player, ["summon", "index", "profile"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("index")
        player.reset_stats()
        log.clear_log()
        player.set_activity("index")
        return render(request, self.template_name, {"player": player})


class DungeonView(LoginRequiredMixin, generic.ListView):

    template_name = "qa_rpg/dungeon.html"

    def get(self, request):
        player = Player.objects.get(user=request.user)

        check_url = check_player_activity(player, ["index", "dungeon"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("dungeon")
        log = get_player_log(player)
        return render(request, self.template_name, {"logs": log.split_log, "player": player})


def action(request):

    player = Player.objects.get(user=request.user)
    log = get_player_log(player)
    event = random.random()

    check_url = check_player_activity(player, ["dungeon"])
    if check_url is not None:
        return redirect(check_url)

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


class BattleView(LoginRequiredMixin, generic.DetailView):

    template_name = 'battle.html'

    def get(self, request):
        player = Player.objects.get(user=request.user)

        check_url = check_player_activity(player, ["battle", "found monster"])
        if check_url is not None:
            return redirect(check_url)

        if difflib.get_close_matches(player.activity, ["battle"]):
            question_id = int(player.activity[6:])
        else:
            question_id = random.choice(Question.objects.filter(~Q(owner=request.user))
                                        .values_list("id", flat=True))
        question = Question.objects.get(pk=question_id)

        player.set_activity(f"battle{question_id}")
        return render(request, "qa_rpg/battle.html", {"question": question, "player": player})


def check(request, question_id):

    question = Question.objects.get(pk=question_id)
    player = Player.objects.get(user=request.user)
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
            player.update_player_stats(dungeon_currency=earn_coins, luck=0.03)
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
    for i in range(1, 6):
        if i * 20 <= damage < (i + 1) * 20:
            return random.randrange(start=i*8, stop=(i + 1)*8, step=1)
    return 50


class SummonView(LoginRequiredMixin, generic.DetailView):

    template_name = "summon.html"

    def get(self, request):
        player = Player.objects.get(user=request.user)

        check_url = check_player_activity(player, ["summon", "index"])
        if check_url is not None:
            return redirect(check_url)

        fee = 150 + Question.objects.filter(owner=request.user).count() * 20
        player.set_activity("summon4")
        return render(request, "qa_rpg/summon.html", {"amount": range(4), "fee": fee,
                                                      "category": CATEGORY, "player": player})  # fixed 4 choices for now


def create(request):
    player = Player.objects.get(user=request.user)

    try:
        question_text = request.POST['question']
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
                                       owner=request.user)
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

    def get(self, request):
        player = Player.objects.get(user=request.user) # dummy player
        questions = Question.objects.filter(owner=player.user)

        check_url = check_player_activity(player, ["index", "profile"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("profile")

        return render(request, self.template_name, {"player": player, "questions": questions})


def claim_coin(request, question_id):
    player = Player.objects.get(user=request.user)
    questions = Question.objects.get(pk=question_id)

    player.currency += questions.currency
    questions.currency = 0
    player.save()
    questions.save()
    return redirect('qa_rpg:profile')



