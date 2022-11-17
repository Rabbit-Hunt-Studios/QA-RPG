"""Module containing view classes."""
import random
import difflib
from django.utils.decorators import method_decorator
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.views.decorators.cache import never_cache

from .models import Question, Choice, Player, Log, Inventory, ReportAndCommend
from .dialogue import Dialogue
from .template_question import TemplateCatalog
from .items_catalog import ItemCatalog

TREASURE_AMOUNT = [15, 30, 35, 40, 45, 50, 60, 69]
TREASURE_THRESHOLD = 0.55
ITEM_CHANCE = 0.37
MAX_QUESTIONS_SEEN = 50
EXIT_CHECK = '-9999'
UPGRADE = {
    "max_hp": 20,
    "max_earn": 2,
    "rate_earn": 1,
    "awake": 1,
    "inventory": 3
}
UPGRADE_BASE = {
    "max_hp": 100,
    "max_earn": 20,
    "rate_earn": 5
}
UPGRADE_RATE = {
    "max_hp": 100,
    "max_earn": 10,
    "rate_earn": 5
}
MAX_AWAKEN = 3

item_list = ItemCatalog()
question_templates = TemplateCatalog()


def get_player(user: User):
    """
    Check if Player of the user exists, if not create a new one.
    :param user: logged in User
    :return: Player object
    """
    try:
        player = Player.objects.get(user=user)
    except Player.DoesNotExist:
        player = Player.objects.create(user=user)
        player.save()
    return player


def get_log(player: Player):
    """
    Check if Log of the player exists, if not create a new one.
    :param player:
    :return: Log object
    """
    try:
        log = Log.objects.get(player=player)
    except Log.DoesNotExist:
        log = Log.objects.create(player=player)
        log.save()
    return log


def get_inventory(player: Player):
    """
    Check if Inventory of the player exists, if not create a new one.
    :param player:
    :return: Inventory object
    """
    try:
        inventory = Inventory.objects.get(player=player)
    except Inventory.DoesNotExist:
        inventory = Inventory.objects.create(player=player)
        inventory.update_inventory({0: 5}, "player")
        inventory.update_templates({0: 1, 1: 1})
        inventory.save()
    return inventory


def check_player_activity(player: Player, allowed_activity: list):
    """
    Check player activity if the player is allowed to be in this page.
    :param player: Player
    :param allowed_activity:
    :return: url that player should be in
    """
    if not difflib.get_close_matches(player.activity, allowed_activity):
        if difflib.get_close_matches(player.activity, ["battle", "summon"]):
            return f"qa_rpg:{player.activity[:6]}"
        return f"qa_rpg:{player.activity}"
    return None


def get_available_template(inventory: Inventory):
    """
    Return dictionary containing amount of each available templates.
    :param inventory: Inventory object
    :return: dict of available template
    """
    available = {}
    for index, value in inventory.get_templates().items():
        available[" ".join(question_templates.get_template(index)) + " ?"] = [index, value]
    return available


class HomeView(generic.TemplateView):
    """Home page of application."""

    template_name = 'qa_rpg/homepage.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Home page"""
        return render(request, self.template_name)


class IndexView(LoginRequiredMixin, generic.TemplateView):
    """Index page of application."""
    template_name = 'qa_rpg/index.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Index page."""
        player = get_player(request.user)
        log, inventory = get_log(player), get_inventory(player)

        check_url = check_player_activity(player=player,
                                          allowed_activity=["summon", "index",
                                                            "profile", "shop", "select"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity("index")
        player.reset_stats()
        log.clear_log()
        log.clear_question()
        return render(request, self.template_name, {"player": player})


class DungeonView(LoginRequiredMixin, generic.ListView):
    """Dungeon page of application."""

    template_name = "qa_rpg/dungeon.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Dungeon page."""
        player = get_player(request.user)
        log = get_log(player)

        check_url = check_player_activity(player, ["select_items", "dungeon"])
        if check_url is not None:
            return redirect(check_url)

        if EXIT_CHECK in log.split_log("question"):
            log.add_log("The coast is clear, you may now exit the dungeon.")

        player.set_activity("dungeon")
        return render(request, self.template_name, {"logs": log.split_log("text"), "player": player})


@never_cache
def action(request):
    """
    Check if player found monster in walking or exiting.
    :param request: HTML request
    :return: redirect player to dungeon or index page
    """
    player = get_player(request.user)
    log, inventory = get_log(player), get_inventory(player)
    event = random.random()
    player_action = request.POST['action']

    if player_action == "walk":

        if EXIT_CHECK in log.split_log("question"):
            log.remove_question(EXIT_CHECK)

        if player.luck >= TREASURE_THRESHOLD and event <= (player.luck - TREASURE_THRESHOLD):
            log.add_log(f"You found a treasure chest.")
            player.update_player_stats(luck=-(player.luck - TREASURE_THRESHOLD))
            return redirect("qa_rpg:treasure")

        if event <= player.luck:
            log.add_log(Dialogue.MONSTER.get_text + Dialogue.BATTLE_DIALOGUE.get_text)
            player.set_activity("found monster")
            return redirect("qa_rpg:battle")

        log.add_log(Dialogue.WALK_DIALOGUE.get_text)
        player.update_player_stats(luck=0.02)
        return redirect("qa_rpg:dungeon")

    else:
        if event <= 0.5 and EXIT_CHECK not in log.split_log("question"):
            log.add_log("A " + Dialogue.MONSTER.get_text + " is blocking the dungeon exit.")
            log.add_question(EXIT_CHECK)
            player.set_activity("found monster")
            return redirect("qa_rpg:battle")

        player.set_activity("index")
        player.add_dungeon_currency()
        inventory.reset_inventory()
        return redirect("qa_rpg:index")


class TreasureView(LoginRequiredMixin, generic.DetailView):
    """Treasure page of application."""
    template_name = "qa_rpg/treasure.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Treasure page."""
        player = get_player(request.user)

        check_url = check_player_activity(player, ["dungeon", "treasure"])
        if check_url is not None:
            return redirect(check_url)

        player.set_activity(f"treasure")
        return render(request, self.template_name, {"player": player})


@never_cache
def treasure_action(request):
    """
    Check if the player Choose between pick up item from treasure or walk away.
    :param request: HTML request
    :return: redirect to dungeon page
    """
    player = get_player(request.user)
    log, inventory = get_log(player), get_inventory(player)
    event = random.random()

    if request.POST['action'] != "pick up":
        log.add_log(f"You walk away from the treasure chest.")

    elif (player.luck * ITEM_CHANCE) >= event:
        item_id = random.choice(item_list.get_chest_items())
        random_item = item_list.get_item(item_id)
        log.add_log(f"You got the item '{str(random_item)}' from the chest !")
        dungeon_inventory = inventory.get_inventory("dungeon")
        try:
            dungeon_inventory[item_id] += 1
        except KeyError:
            dungeon_inventory[item_id] = 1
        inventory.update_inventory(dungeon_inventory, "dungeon")

    elif player.luck >= event:
        coin_amount = random.choice(TREASURE_AMOUNT)
        log.add_log(f"You found {coin_amount} coins in treasure chest.")
        player.update_player_stats(dungeon_currency=coin_amount)

    else:
        damages = random.randint(1, 10)
        player.update_player_stats(health=-damages)

        if player.check_death():
            messages.error(request, "You lost consciousness in the dungeons.")
            return render(request, "qa_rpg/index.html", {'player': player})

        log.add_log(f"The chest turned out to be a mimic!! You lose {damages} health points.")

    player.set_activity("dungeon")
    return redirect("qa_rpg:dungeon")


class BattleView(LoginRequiredMixin, generic.DetailView):
    """Battle page of application."""
    template_name = 'battle.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Battle page."""
        player = get_player(request.user)
        log, inventory = get_log(player), get_inventory(player)

        check_url = check_player_activity(player, ["battle", "found monster"])
        if check_url is not None:
            return redirect(check_url)

        if difflib.get_close_matches(player.activity, ["battle"]):
            question_id = int(player.activity[6:])
        else:
            seen_question = log.split_log("question")
            report_question = log.split_log("report")
            unwanted_questions_id = seen_question + report_question

            unwanted_queryset = Question.objects.exclude(id__in=unwanted_questions_id)
            unseen_player_questions = unwanted_queryset.filter(~Q(owner=request.user),
                                                               category='player',
                                                               enable=True).values_list("id", flat=True)

            amount_seen = len(seen_question)
            if amount_seen > MAX_QUESTIONS_SEEN:
                log.clear_question()

            if ((amount_seen % 10) != 0) or amount_seen == 0 or len(unseen_player_questions) == 0:
                question_id = random.choice(unwanted_queryset.filter(~Q(owner=request.user),
                                                                     enable=True).values_list('id', flat=True))

            else:
                question_id = random.choice(unseen_player_questions)

            log.add_question(question_id)

        question = Question.objects.get(pk=question_id)
        player.set_activity(f"battle{question_id}")
        items = {}
        for key, value in inventory.get_inventory("dungeon").items():
            player_item = item_list.get_item(key)
            items[str(player_item)] = [key, value, player_item.description, player_item.effect]
        status = ""
        if player.status != "":
            status += str(item_list.get_item(int(player.status)))
        return render(request, "qa_rpg/battle.html", {"question": question, "player": player,
                                                      "items": items,
                                                      "status": status})


@never_cache
def item(request):
    """
    Check the items that the player chooses to use.
    :param request: HTML request
    :return: redirect player to battle page
    """
    try:
        index = int(request.POST['item'])
    except KeyError:
        messages.error(request, "You select an item to use.")
        return redirect("qa_rpg:battle")

    player = get_player(request.user)
    log, inventory = get_log(player), get_inventory(player)

    used_item = item_list.get_item(index)
    dungeon_inventory = inventory.get_inventory("dungeon")
    dungeon_inventory[index] -= 1
    inventory.update_inventory(dungeon_inventory, "dungeon")
    log.add_log("You used an item: " + str(used_item) + " !")

    health_add = used_item.health_modifier(player.max_hp)
    player.update_player_stats(health=health_add)
    if health_add > 0:
        log.add_log(f"You healed {health_add} health points.")
    elif health_add < 0:
        log.add_log(f"You sacrificed {-health_add} health points.")
        if player.check_death():
            messages.error(request, "You lost consciousness in the dungeons.")
            return redirect("qa_rpg:index")

    player.status = str(index)
    player.save()

    return redirect("qa_rpg:battle")


@never_cache
def check(request, question_id):
    """
    Checks the player's answer and checks the results of the item used by the player.
    :param request: HTML request
    :param question_id:
    :return: redirect player to right page
    """
    question = Question.objects.get(pk=question_id)
    player = get_player(request.user)
    log, inventory = get_log(player), get_inventory(player)
    one_user_per_report(request, question, log)
    set_question_activation(question_id)

    try:
        check_choice = Choice.objects.get(pk=request.POST['choice'])
    except KeyError:
        messages.error(request, "You didn't select a attack move.")
        return redirect("qa_rpg:battle")

    if player.status == "":
        applied_item = item_list.get_item(999)
    else:
        applied_item = item_list.get_item(int(player.status))
    player.status = ""
    player.save()

    if check_choice.correct_answer:
        log.add_log(Dialogue.WIN_DIALOGUE.get_text)
        chance = 0.23
        if (applied_item.item_modifier(1) != 0 or chance >= random.random()) and not applied_item.coin_modifier(100):
            item_id = random.choice(item_list.get_cursed_items())
            random_item = item_list.get_item(item_id)
            dungeon_inventory = inventory.get_inventory("dungeon")
            amount = 1 + applied_item.item_modifier(1)
            try:
                dungeon_inventory[item_id] += amount
            except KeyError:
                dungeon_inventory[item_id] = amount
            log.add_log(f"You loot the {amount} '{str(random_item)}(s)' from the monster's corpse !")
            inventory.update_inventory(dungeon_inventory, "dungeon")
        else:
            earn_coins = get_coins(question.damage)
            bonus = applied_item.coin_modifier(earn_coins)
            earn_coins += bonus
            if bonus > 0:
                log.add_log(f"You earn {earn_coins} coins ({bonus} bonus coins).")
            else:
                log.add_log(f"You earn {earn_coins} coins.")
            player.update_player_stats(dungeon_currency=earn_coins, luck=0.03)

    else:
        log.add_log(Dialogue.LOSE_DIALOGUE.get_text)
        nullified = applied_item.damage_modifier(question.damage)
        if nullified > 0:
            log.add_log(f"{nullified} damage from monster was blocked by your item.")
        elif nullified < 0:
            log.add_log(f"{-nullified} damage suffered from cursed item.")
        player.update_player_stats(health=-(question.damage - nullified))
        question.add_coin()
        if player.check_death():
            messages.error(request, "You lost consciousness in the dungeons.")
            return redirect("qa_rpg:index")

        log.add_log(f"You lose {question.damage - nullified} health points.")

    player.set_activity("dungeon")
    return redirect("qa_rpg:dungeon")


@never_cache
def run_away(request, question_id):
    """
    Randomize whether the player can escape from the question or not.
    :param request: HTML request
    :param question_id:
    :return: render or redirect player to battle or dungeon page
    """
    question = Question.objects.get(pk=question_id)
    player = get_player(request.user)
    log, inventory = get_log(player), get_inventory(player)

    one_user_per_report(request, question, log)
    set_question_activation(question_id)

    if player.status == "":
        applied_item = item_list.get_item(999)
    else:
        applied_item = item_list.get_item(int(player.status))
    player.status = ""
    player.save()

    if random.random() >= player.luck - applied_item.escape_modifier(player.luck):
        log.add_log(Dialogue.RUN_DIALOGUE.get_text)
        player.set_activity("dungeon")
        return redirect("qa_rpg:dungeon")

    run_fail = Dialogue.RUN_FAIL_DIALOGUE.get_text
    log.add_log(run_fail)
    player.update_player_stats(health=-(question.damage - applied_item.damage_modifier(question.damage)))
    question.add_coin()
    if player.check_death():
        messages.error(request, "You lost consciousness in the dungeons.")
        return redirect("qa_rpg:index")

    messages.error(request, run_fail)
    items = {}
    for key, value in inventory.get_inventory("dungeon").items():
        player_item = item_list.get_item(key)
        items[str(player_item)] = [key, value, player_item.description, player_item.effect]
    if player.status == "":
        status = ""
    else:
        status = str(item_list.get_item(int(player.status)))
    return render(request,
                  'qa_rpg/battle.html',
                  {'question': question, 'player': player, "status": status, "items": items})


def add_reports_or_commends(request, question, log):
    """
    Add a report or commend of the question.
    :param request: HTML request
    :param question: question object
    :param log: player log object
    """
    if request.POST['option'] == 'report':
        report = ReportAndCommend.objects.create(question=question, user=request.user, vote=0)
        report.save()
        log.add_report_question(question.id)
    elif request.POST['option'] == 'commend':
        commend = ReportAndCommend.objects.create(question=question, user=request.user, vote=1)
        commend.save()


def one_user_per_report(request, question, log):
    """
    One player can only report or commend once.
    :param request: HTML request
    :param question: question object
    :param log: player log object
    """
    user = request.user
    try:
        option_select = ReportAndCommend.objects.get(question=question, user=user)
        if request.POST['option'] == 'report':
            option_select.vote = 0
            option_select.save()
            log.add_report_question(question.id)
        elif request.POST['option'] == 'commend':
            option_select.vote = 1
            option_select.save()
    except ReportAndCommend.DoesNotExist:
        add_reports_or_commends(request, question, log)


def set_question_activation(question_id):
    """
    Check the question of the player whether to disable the question or not.
    :param question_id:
    """
    question = Question.objects.get(pk=question_id)
    report_num = question.report
    commend_num = question.commend
    report_score = report_num
    commend_score = commend_num * 0.5
    limit = 7
    if question.owner != User.objects.get(pk=2):
        if report_score - commend_score > limit:
            question.enable = False
            question.save()


def get_coins(damage: int):
    """
    Calculate the amount of currency the player receives from the damage of the question.
    :param damage: question damage
    :return: coin that player earn.
    """
    start = 20
    end = 20
    for i in range(0, 3):
        start += i * 5
        end += (i + 1) * 5
        if start <= damage < end:
            return random.randrange(start=(i * 10) + 6, stop=(i + 1) * 10, step=1)
    return 50  # pragma: no cover


class TemplateChooseView(LoginRequiredMixin, generic.DetailView):
    """Template page of application."""
    template_name = "qa_rpg/template_choose.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Template choose page."""
        player = get_player(request.user)
        inventory = get_inventory(player)

        check_url = check_player_activity(player, ["summon", "index"])
        if check_url is not None:
            return redirect(check_url)

        available = get_available_template(inventory)

        return render(request, self.template_name, {"selection": available})


@never_cache
def choose(request):
    """
    Save selected template to player activity.
    :param request: HTML request
    :return: redirect to summon page
    """
    player = get_player(request.user)
    player.set_activity(f"choose{request.GET['index']}")
    return redirect("qa_rpg:summon")


class SummonView(LoginRequiredMixin, generic.DetailView):
    """Summon page of application."""
    template_name = "summon.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Summon page."""
        player = get_player(request.user)

        check_url = check_player_activity(player, ["choose", "summon"])
        if check_url is not None:
            return redirect(check_url)

        if difflib.get_close_matches(player.activity, ['choose']):
            template_index = int(player.activity[6:])
            player.set_activity(f"summon4 {template_index}")
        else:
            template_index = int(player.activity.split(" ")[1])
        return render(request, "qa_rpg/summon.html",
                      {"question": question_templates.get_template(template_index),
                       "id": template_index,
                       "amount": range(4),
                       "fee": "50",
                       "player": player})


@never_cache
def create(request):
    """
    Create Player question from template that player select.
    :param request: HTML select
    :return: redirect to index page if create success but if it fails to create redirect to summon page
    """
    player = get_player(request.user)
    inventory = get_inventory(player)

    summon_fee = int(request.POST['fee'])
    if summon_fee >= player.currency:
        messages.error(request, "You don't have enough coins to summon a monster.")
        return redirect("qa_rpg:summon")

    try:
        question_text = ''
        if int(player.activity.split(" ")[1]) >= 100:
            question_text += request.POST['question0']
            question_text += request.POST['question1']
        else:
            for i in range(4):
                question_text += request.POST[f'question{i}']
        if question_text[-1] != "?":
            question_text += "?"
        choices = {}
        correct_index = int(request.POST['index'])
        for num in range(int(player.activity.split(" ")[0][6:])):
            if num == correct_index:
                choices[request.POST[f'choice{num}']] = True
            else:
                choices[request.POST[f'choice{num}']] = False
    except KeyError:
        messages.error(request, "Please fill in every field and select a correct answer.")
        return redirect("qa_rpg:summon")

    question = Question.objects.create(question_text=question_text,
                                       owner=request.user, category="player",
                                       max_currency=player.question_max_currency,
                                       rate=player.question_rate_currency)
    question.save()
    for choice_text in choices.keys():
        choice = Choice.objects.create(choice_text=choice_text,
                                       correct_answer=choices[choice_text],
                                       question=question)
        choice.save()
    player.set_activity("index")
    messages.success(request, "Successfully summoned a new monster.")
    player.currency -= summon_fee
    owned = inventory.get_templates()
    owned[int(request.POST["template_id"])] -= 1
    inventory.update_templates(owned)
    player.save()
    return redirect('qa_rpg:index')


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    """Profile page of application."""
    template_name = 'qa_rpg/profile.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Profile page."""
        player = get_player(request.user)
        inventory = get_inventory(player)
        questions = Question.objects.filter(owner=player.user)

        check_url = check_player_activity(player, ["index", "profile", "upgrade"])
        if check_url is not None:
            return redirect(check_url)

        player_inventory = []
        for key, val in inventory.get_inventory("player").items():
            player_item = item_list.get_item(key)
            player_inventory.append([str(player_item), val, player_item.description, player_item.effect])

        check_items = True
        player.set_activity("profile")
        return render(request, self.template_name, {"player": player, "questions": questions,
                                                    "inventory": player_inventory, "check": check_items})


@never_cache
def claim_coin(request, question_id):
    """
    Player can earn money from player generated questions
    :param request: HTML request
    :param question_id:
    :return: redirect to profile page
    """
    player = get_player(request.user)
    questions = Question.objects.get(pk=question_id)

    player.currency += questions.currency
    questions.currency = 0
    player.save()
    questions.save()
    return redirect('qa_rpg:profile')


@never_cache
def select(request):
    """
    When a player browses the template inventory
    :param request: HTML request
    :return: redirect to profile page
    """
    if request.POST["select"] == "template":
        template_name = 'qa_rpg/profile.html'

        player = get_player(request.user)
        inventory = get_inventory(player)
        questions = Question.objects.filter(owner=player.user)
        template = get_available_template(inventory)

        check_items = False
        return render(request, template_name, {"player": player, "questions": questions,
                                               "template": template, "check": check_items})
    else:
        return redirect("qa_rpg:profile")


class ShopView(LoginRequiredMixin, generic.DetailView):
    """Shop page of application."""
    template_name = "qa_rpg/shop.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Shop page."""
        player = get_player(request.user)

        check_url = check_player_activity(player, ["index", "shop"])
        if check_url is not None:
            return redirect(check_url)

        items = item_list.get_store_items()

        template = {}
        for index in question_templates.get_all_templates().keys():
            template[" ".join(question_templates.get_template(index)) + " ?"] = [
                question_templates.get_price(index), index]

        player.set_activity("shop")
        return render(request, self.template_name, {"player": player, "template": template, "items": items})


@never_cache
def buy(request):
    """
    Buy an item or template from the store.
    :param request:
    :return:
    """
    player = get_player(request.user)
    inventory = get_inventory(player)

    player_template = inventory.get_templates()
    player_item = inventory.get_inventory("player")
    amount = int(request.POST["amount"])
    try:
        template = int(request.POST["index"])
        price = question_templates.get_price(template)
        if price * amount >= player.currency:
            messages.error(request, "You don't have enough coins to purchase.")
            return redirect("qa_rpg:shop")

        try:
            player_template[template] += amount
        except KeyError:
            player_template[template] = amount
        inventory.update_templates(player_template)
        player.currency -= price * amount
        player.save()

    except ValueError:
        items = request.POST["index"][1:-1].split(",")
        if int(items[1]) * amount > player.currency:
            messages.error(request, "You don't have enough coins to purchase.")
            return redirect("qa_rpg:shop")

        try:
            player_item[int(items[0])] += amount
        except KeyError:
            player_item[int(items[0])] = amount
        inventory.update_inventory(player_item, "player")
        player.currency -= int(items[1]) * amount
        player.save()

    messages.success(request, "Purchase Successful")
    return redirect('qa_rpg:shop')


class UpgradeView(LoginRequiredMixin, generic.DetailView):
    """Upgrade page of application."""
    template_name = "qa_rpg/upgrade.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Upgrade page."""
        player = get_player(request.user)

        check_url = check_player_activity(player, ["profile", "upgrade", "select_items"])
        if check_url is not None:
            return redirect(check_url)

        price = [100 + (int((player.max_hp - 100) / 20) * 50),
                 100 + (int((player.question_max_currency - 20) / 2) * 50),
                 100 + (int((player.question_rate_currency - 5)) * 50),
                 200 + (player.awake * 200)]

        upgrade_list = [UPGRADE_BASE["max_hp"] + (UPGRADE_RATE["max_hp"] * (player.awake + 1)),
                        UPGRADE_BASE["max_earn"] + (UPGRADE_RATE["max_earn"] * (player.awake + 1)),
                        UPGRADE_BASE["rate_earn"] + (UPGRADE_RATE["rate_earn"] * (player.awake + 1))]

        upgrade_check = [(player.max_hp < upgrade_list[0]),
                         (player.question_max_currency < upgrade_list[1]),
                         (player.question_rate_currency < upgrade_list[2]),
                         (player.awake < MAX_AWAKEN)]

        awaken_rate = (0.5 - (0.1 * player.awake)) * 100

        player.set_activity("upgrade")
        return render(request, self.template_name, {"player": player, "price": price,
                                                    "upgrade_list": upgrade_list,
                                                    "upgrade_check": upgrade_check,
                                                    "awaken_rate": awaken_rate})


@never_cache
def upgrade(request):
    """
    Upgrade one particular player stat.
    :param request:
    :return:
    """
    player = get_player(request.user)
    player_question = Question.objects.filter(owner=request.user)
    price = int(request.POST["price"])
    if player.currency >= price:
        player.currency -= price
        if request.POST["upgrade"] == "max_hp":
            if player.max_hp + UPGRADE["max_hp"] <= UPGRADE_BASE["max_hp"] + (UPGRADE_RATE["max_hp"] * (player.awake + 1)):
                player.max_hp += UPGRADE["max_hp"]

        elif request.POST["upgrade"] == "max_earn":
            if player.question_max_currency + UPGRADE["max_earn"] <= UPGRADE_BASE["max_earn"] + (UPGRADE_RATE["max_earn"] * (player.awake + 1)):
                player.question_max_currency += UPGRADE["max_earn"]

        elif request.POST["upgrade"] == "rate_earn":
            if player.question_rate_currency + UPGRADE["rate_earn"] <= UPGRADE_BASE["rate_earn"] + (UPGRADE_RATE["rate_earn"] * (player.awake + 1)):
                player.question_rate_currency += UPGRADE["rate_earn"]

        for question in player_question:
            question.max_currency = player.question_max_currency
            question.rate = player.question_rate_currency
            question.save()
        messages.success(request, "Upgrade Successful")
    else:
        messages.error(request, "You don't have enough coins to upgrade.")

    player.save()
    return redirect('qa_rpg:upgrade')


@never_cache
def awake(request):
    """
    Randomize a chance to add 1 to awaken level.
    :param request:
    :return:
    """
    player = get_player(request.user)
    inventory = get_inventory(player)

    event = random.random()
    price = int(request.POST["price"])
    if player.currency >= price:
        player.currency -= price
        if event < 0.5 - (0.1 * player.awake):
            player.awake += UPGRADE["awake"]
            inventory.max_inventory += UPGRADE["inventory"]
            messages.success(request, "Awaken Successful")
        else:
            messages.error(request, "Awaken Fail")
    else:
        messages.error(request, "You don't have enough coins to Awaken.")

    player.save()
    inventory.save()
    return redirect('qa_rpg:upgrade')


class SelectItemsView(LoginRequiredMixin, generic.DetailView):
    """Select items page of application."""
    template_name = 'qa_rpg/select_items.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        """Return Select items page."""
        player = get_player(request.user)
        inventory = get_inventory(player)

        check_url = check_player_activity(player, ["index", "select_items"])
        if check_url is not None:
            return redirect(check_url)

        player_inventory = []
        for key, val in inventory.get_inventory("player").items():
            player_item = item_list.get_item(key)
            player_inventory.append([key, str(player_item), val, player_item.description, player_item.effect])

        dungeon_inventory = []
        for key, val in inventory.get_inventory("dungeon").items():
            dungeon_item = item_list.get_item(key)
            dungeon_inventory.append([key, str(dungeon_item), val, dungeon_item.description, dungeon_item.effect])
        dungeon_inventory_num = [len(inventory.get_inventory("dungeon")), inventory.max_inventory]

        player.set_activity("select_items")
        check_items = False
        return render(request, self.template_name, {"player": player,
                                                    "inventory": player_inventory, "check": check_items,
                                                    "dungeon_inventory": dungeon_inventory,
                                                    "dungeon_inventory_num": dungeon_inventory_num})


@never_cache
def select_items(request):
    """
    Add items from normal inventory to dungeon inventory.
    :param request: HTML request
    :return:
    """
    player = get_player(request.user)
    inventory = get_inventory(player)
    amount = int(request.POST["amount"])
    dungeon_inventory = inventory.get_inventory("dungeon")
    player_current_inventory = inventory.get_inventory("player")
    if len(dungeon_inventory) < inventory.max_inventory and request.POST["select"][-1] == "1":
        item_id = int(request.POST["select"][:-1])
        if player_current_inventory[item_id] - amount >= 0:
            try:
                dungeon_inventory[item_id] += amount
                player_current_inventory[item_id] -= amount
            except KeyError:
                dungeon_inventory[item_id] = amount
                player_current_inventory[item_id] -= amount
        else:
            messages.error(request, "You don't have that much items.")
    elif request.POST["select"][-1] == "2":
        item_id = int(request.POST["select"][:-1])
        if dungeon_inventory[item_id] - amount >= 0:
            try:
                player_current_inventory[item_id] += amount
                dungeon_inventory[item_id] -= amount
            except KeyError:
                player_current_inventory[item_id] = amount
                dungeon_inventory[item_id] -= amount
            inventory.update_inventory(dungeon_inventory, "dungeon")
            inventory.update_inventory(player_current_inventory, "player")
        else:
            messages.error(request, "You don't have that much items.")
    else:
        messages.error(request, "Your bag is full.")

    inventory.update_inventory(dungeon_inventory, "dungeon")
    inventory.update_inventory(player_current_inventory, "player")

    return redirect('qa_rpg:select_dg')
