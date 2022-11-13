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

from .models import Question, Choice, Player, Log, Inventory, ReportAndCommend
from .dialogue import Dialogue
from .template_question import TemplateCatalog
from .items_catalog import ItemCatalog

TREASURE_AMOUNT = [15, 30, 35, 40, 45, 50, 60, 69]
TREASURE_THRESHOLD = 0.5
CATEGORY = ['General Knowledge', 'Entertainment', 'Science', 'Math',
            'History', 'Technology', 'Sport']
ITEM_CHANCE = 0.34
EXIT_CHECK = '9999'
item_list = ItemCatalog()


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
            inventory.update_templates({0: 1, 1: 1})
            inventory.update_inventory({0: 5}, "player")
            inventory.save()
            continue
    return player, log, inventory


def check_player_activity(player: Player, activity: list):
    if not difflib.get_close_matches(player.activity, activity):
        if difflib.get_close_matches(player.activity, ["battle", "summon"]):
            return f"qa_rpg:{player.activity[:6]}"
        return f"qa_rpg:{player.activity}"
    return None


def get_available_template(inventory: Inventory):
    available = {}
    for index, value in inventory.get_templates().items():
        available[" ".join(TemplateCatalog.TEMPLATES.get_template(index)) + " ?"] = [index, value]
    return available


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

        check_url = check_player_activity(player, ["summon", "index", "profile", "shop", "select"])
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
        check_url = check_player_activity(player, ["select", "dungeon"])
        if check_url is not None:
            return redirect(check_url)

        if EXIT_CHECK in log.split_log("question"):
            log.add_log("The coast is clear, you may now exit the dungeon.")  # HELP change log

        player.set_activity("dungeon")
        return render(request, self.template_name, {"logs": log.split_log("text"), "player": player})


@never_cache
def action(request):
    player, log, inventory = get_player(request.user)
    event = random.random()

    if request.POST['action'] == "walk":

        if EXIT_CHECK in log.split_log("question"):
            log.remove_question(EXIT_CHECK)

        url = "qa_rpg:dungeon"
        if player.luck >= TREASURE_THRESHOLD and event <= (player.luck - TREASURE_THRESHOLD):
            log.add_log(f"You found a treasure chest")
            player.update_player_stats(luck=-(player.luck - TREASURE_THRESHOLD))
            url = "qa_rpg:treasure"
        elif event <= player.luck:
            url = found_monster(request)
        else:
            log.add_log(Dialogue.WALK_DIALOGUE.get_text)
            player.update_player_stats(luck=0.02)
        return redirect(url)
    else:
        if event <= 0.5 and EXIT_CHECK not in log.split_log("question"):
            return redirect(found_monster(request))
        else:
            player.set_activity("index")
            player.status = ""
            player.add_dungeon_currency()
            inventory.reset_inventory()
            return redirect("qa_rpg:index")


def found_monster(request):
    player, log, inventory = get_player(request.user)
    if request.POST['action'] == "walk":
        log.add_log(Dialogue.MONSTER.get_text + Dialogue.BATTLE_DIALOGUE.get_text)
    else:
        log.add_log("A " + Dialogue.MONSTER.get_text + " is blocking the dungeon exit.")
        log.add_question(EXIT_CHECK)

    player.set_activity("found monster")
    return "qa_rpg:battle"


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
            if (player.luck * ITEM_CHANCE) >= event:
                item_id = random.choice(item_list.get_chest_items())
                random_item = item_list.get_item(item_id)
                log.add_log(f"You got the item '{str(random_item)}' from the chest !")
                dungeon_inventory = inventory.get_inventory("dungeon")
                try:
                    dungeon_inventory[item_id] += 1
                except KeyError:
                    dungeon_inventory[item_id] = 1
                inventory.update_inventory(dungeon_inventory, "dungeon")
            else:
                coins = random.choice(TREASURE_AMOUNT)
                log.add_log(f"You found {coins} coins in treasure chest.")
                player.update_player_stats(dungeon_currency=coins)
        else:
            log.add_log("Oh No!! Mimic chest bite your leg")
            damages = random.randint(1, 10)
            player.update_player_stats(health=-damages)
            if player.check_death():
                inventory.clear_dungeon_inventory()
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

        check_url = check_player_activity(player, ["battle", "found monster"])
        if check_url is not None:
            return redirect(check_url)

        if difflib.get_close_matches(player.activity, ["battle"]):
            question_id = int(player.activity[6:])
        else:
            seen_question = log.split_log("question")
            report_question = log.split_log("report")
            filter_question = seen_question + report_question
            player_question_amount = Question.objects.filter(~Q(owner=request.user), category='player',
                                                             enable=True).count()
            amount = len(log.split_log("question"))

            if amount > 30:
                log.clear_question()
            try:
                if ((amount % 10) != 0) or amount == 0:
                    question_id = random.choice(
                        Question.objects.exclude(id__in=filter_question).filter(~Q(owner=request.user), enable=True)
                            .values_list('id', flat=True))
                    log.add_question(question_id)
                else:
                    question_id = random.choice(
                        Question.objects.exclude(id__in=filter_question).filter(~Q(owner=request.user),
                                                                                category='player', enable=True)
                            .values_list("id", flat=True))
                    log.add_question(question_id)
            except IndexError:
                question_id = random.choice(
                    Question.objects.exclude(id__in=seen_question).filter(~Q(owner=request.user), enable=True)
                        .values_list('id', flat=True))
                log.add_question(question_id)
        question = Question.objects.get(pk=question_id)
        player.set_activity(f"battle{question_id}")
        items = {}
        for key, value in inventory.get_inventory("dungeon").items():
            items[str(item_list.get_item(key))] = [key, value]
        if player.status == "":
            status = ""
        else:
            status = str(item_list.get_item(int(player.status)))
        return render(request, "qa_rpg/battle.html", {"question": question, "player": player,
                                                      "items": items,
                                                      "status": status})


@never_cache
def item(request):
    player, log, inventory = get_player(request.user)
    try:
        index = int(request.POST['item'])
        used_item = item_list.get_item(index)
        dungeon_inventory = inventory.get_inventory("dungeon")
        dungeon_inventory[index] -= 1
        inventory.update_inventory(dungeon_inventory, "dungeon")
        log.add_log("You used an item: " + str(used_item) + " !")

        healing = used_item.health_modifier(player.max_hp)
        player.update_player_stats(health=healing)
        if healing > 0:
            log.add_log(f"You healed {healing} health points.")
        elif healing < 0:
            log.add_log(f"You sacrificed {-healing} health points.")
            if player.check_death():
                inventory.clear_dungeon_inventory()
                player.status = ""
                player.save()
                messages.error(request, "You lost consciousness in the dungeons.")
                return render(request, "qa_rpg/index.html", {'player': player})

        player.status = str(index)
        player.save()
    except KeyError:
        messages.error(request, "No item selected.")

    return redirect("qa_rpg:battle")


@never_cache
def check(request, question_id):
    question = Question.objects.get(pk=question_id)
    player, log, inventory = get_player(request.user)
    one_user_per_report(request, question, log, question_id)
    set_question_activation(question_id)

    try:
        check_choice = Choice.objects.get(pk=request.POST['choice'])

        if player.status == "":
            applied_item = item_list.get_item(999)
        else:
            applied_item = item_list.get_item(int(player.status))
        player.status = ""
        player.save()

        if check_choice.correct_answer:
            log.add_log(Dialogue.WIN_DIALOGUE.get_text)
            chance = 0.225
            if applied_item.coin_modifier(100) != 0:
                chance = 0
            elif applied_item.item_modifier(1):
                chance = 1
            if chance >= random.random():
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
                player.update_player_stats(dungeon_currency=earn_coins, luck=0.04)
            player.set_activity("dungeon")
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
                inventory.clear_dungeon_inventory()
                player.status = ""
                player.save()
                messages.error(request, "You lost consciousness in the dungeons.")
                return render(request, "qa_rpg/index.html", {'player': player})

            log.add_log(f"You lose {question.damage - nullified} health points.")
            player.set_activity("dungeon")

        return redirect("qa_rpg:dungeon")

    except KeyError:
        messages.error(request, "You didn't select a attack move.")
        return redirect("qa_rpg:battle")


@never_cache
def run_away(request, question_id):
    question = Question.objects.get(pk=question_id)
    player, log, inventory = get_player(request.user)

    one_user_per_report(request, question, log, question_id)
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
    else:
        run_fail = Dialogue.RUN_FAIL_DIALOGUE.get_text
        log.add_log(run_fail)
        player.update_player_stats(health=-(question.damage - applied_item.damage_modifier(question.damage)))
        question.add_coin()
        if player.check_death():
            inventory.clear_dungeon_inventory()
            player.status = ""
            player.save()
            messages.error(request, "You lost consciousness in the dungeons.")
            return render(request, "qa_rpg/index.html", {'player': player})

        messages.error(request, run_fail)
        items = {}
        for key, value in inventory.get_inventory("dungeon").items():
            items[str(item_list.get_item(key))] = [key, value]
        if player.status == "":
            status = ""
        else:
            status = str(item_list.get_item(int(player.status)))
        return render(request,
                      'qa_rpg/battle.html',
                      {'question': question,
                       'player': player, "status": status, "items": items})


def add_reports_or_commends(request, question, log, question_id):
    if request.POST['option'] == 'report':
        report = ReportAndCommend.objects.create(question=question, user=request.user, vote=0)
        report.save()
        log.add_report_question(question.id)
    elif request.POST['option'] == 'commend':
        commend = ReportAndCommend.objects.create(question=question, user=request.user, vote=1)
        commend.save()


def one_user_per_report(request, question, log, question_id):
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
    except:
        add_reports_or_commends(request, question, log, question_id)


def set_question_activation(question_id):
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
    start = 20
    end = 20
    for i in range(0, 3):
        start += i * 5
        end += (i + 1) * 5
        if start <= damage < end:
            return random.randrange(start=(i * 9) + 1, stop=(i + 1) * 9, step=1)
    return 50


class TemplateChooseView(LoginRequiredMixin, generic.DetailView):
    template_name = "qa_rpg/template_choose.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["summon", "index"])
        if check_url is not None:
            return redirect(check_url)

        available = get_available_template(inventory)

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

        if difflib.get_close_matches(player.activity, ['choose']):
            template_index = int(player.activity[6:])
            player.set_activity(f"summon4 {template_index}")
        else:
            template_index = int(player.activity.split(" ")[1])
        return render(request, "qa_rpg/summon.html",
                      {"question": TemplateCatalog.TEMPLATES.get_template(template_index),
                       "id": template_index,
                       "amount": range(4),
                       "fee": "50",
                       "player": player})


@never_cache
def create(request):
    player, log, inventory = get_player(request.user)

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
    template_name = 'qa_rpg/profile.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)
        questions = Question.objects.filter(owner=player.user)

        check_url = check_player_activity(player, ["index", "profile", "upgrade"])
        if check_url is not None:
            return redirect(check_url)

        player_inventory = []
        for key, val in inventory.get_inventory("player").items():
            player_inventory.append([str(item_list.get_item(key)), val])

        check_items = True
        player.set_activity("profile")
        return render(request, self.template_name, {"player": player, "questions": questions,
                                                    "inventory": player_inventory, "check": check_items})


@never_cache
def claim_coin(request, question_id):
    player, log, inventory = get_player(request.user)
    questions = Question.objects.get(pk=question_id)

    player.currency += questions.currency
    questions.currency = 0
    player.save()
    questions.save()
    return redirect('qa_rpg:profile')


@never_cache
def select(request):
    if request.POST["select"] == "template":
        template_name = 'qa_rpg/profile.html'

        player, log, inventory = get_player(request.user)
        questions = Question.objects.filter(owner=player.user)
        template = get_available_template(inventory)

        check_items = False
        return render(request, template_name, {"player": player, "questions": questions,
                                               "template": template, "check": check_items})
    else:
        return redirect("qa_rpg:profile")


class ShopView(LoginRequiredMixin, generic.DetailView):
    template_name = "qa_rpg/shop.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["index", "shop"])
        if check_url is not None:
            return redirect(check_url)

        template = {}
        for index in TemplateCatalog.TEMPLATES.value.keys():
            template[" ".join(TemplateCatalog.TEMPLATES.get_template(index)) + " ?"] = [
                TemplateCatalog.TEMPLATES.get_price(index), index]

        player.set_activity("shop")
        return render(request, self.template_name, {"player": player, "template": template})


@never_cache
def buy(request):
    player, log, inventory = get_player(request.user)
    player_template = inventory.get_templates()
    amount = int(request.POST["amount"])
    template = request.POST["index"][1:-1].split(",")
    if int(template[0]) * amount >= player.currency:
        messages.error(request, "You don't have enough coins to purchase.")
        return redirect("qa_rpg:shop")

    try:
        player_template[int(template[1])] += amount
    except:
        player_template[int(template[1])] = amount
    inventory.update_templates(player_template)
    player.currency -= int(template[0]) * amount
    player.save()
    messages.success(request, "Purchase Successful")
    return redirect('qa_rpg:shop')


class UpgradeView(LoginRequiredMixin, generic.DetailView):
    template_name = "qa_rpg/upgrade.html"

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["profile", "upgrade"])
        if check_url is not None:
            return redirect(check_url)

        price = [100 + (int((player.max_hp - 100) / 20) * 50),
                 100 + (int((player.question_max_currency - 20) / 2) * 50),
                 100 + (int((player.question_rate_currency - 5)) * 50),
                 200 + (player.awake * 200)]

        upgrade_list = [100 + (100 * (player.awake + 1)),
                        20 + (10 * (player.awake + 1)),
                        5 + (5 * (player.awake + 1))]

        upgrade_check = [(player.max_hp < upgrade_list[0]),
                         (player.question_max_currency < upgrade_list[1]),
                         (player.question_rate_currency < upgrade_list[2]),
                         (player.awake < 3)]

        awaken_rate = (0.5 - (0.1 * player.awake)) * 100

        player.set_activity("upgrade")
        return render(request, self.template_name, {"player": player, "price": price,
                                                    "upgrade_list": upgrade_list, "upgrade_check": upgrade_check,
                                                    "awaken_rate": awaken_rate})


@never_cache
def upgrade(request):
    player, log, inventory = get_player(request.user)
    player_question = Question.objects.filter(owner=request.user)
    price = int(request.POST["price"])
    if player.currency >= price:
        player.currency -= price
        if request.POST["upgrade"] == "max_hp":
            if player.max_hp + 20 <= 100 + (100 * (player.awake + 1)):
                player.max_hp += 20

        elif request.POST["upgrade"] == "max_earn":
            if player.question_max_currency + 2 <= 20 + (10 * (player.awake + 1)):
                player.question_max_currency += 2

        elif request.POST["upgrade"] == "rate_earn":
            if player.question_rate_currency + 1 <= 5 + (5 * (player.awake + 1)):
                player.question_rate_currency += 1

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
    player, log, inventory = get_player(request.user)
    event = random.random()
    price = int(request.POST["price"])
    if player.currency >= price:
        player.currency -= price
        if event < 0.5 - (0.1 * player.awake):
            player.awake += 1
            inventory.max_inventory += 3
            messages.success(request, "Awaken Successful")
        else:
            messages.error(request, "Awaken Fail")
    else:
        messages.error(request, "You don't have enough coins to Awaken.")

    player.save()
    inventory.save()
    return redirect('qa_rpg:upgrade')


class SelectItemsView(LoginRequiredMixin, generic.DetailView):
    template_name = 'qa_rpg/select_items.html'

    @method_decorator(never_cache, name='self.get')
    def get(self, request):
        player, log, inventory = get_player(request.user)

        check_url = check_player_activity(player, ["index", "select"])
        if check_url is not None:
            return redirect(check_url)

        player_inventory = {}
        for key, val in inventory.get_inventory("player").items():
            player_inventory[key] = [str(item_list.get_item(key)), val]

        dungeon_inventory = {}
        for key, val in inventory.get_inventory("dungeon").items():
            dungeon_inventory[key] = [str(item_list.get_item(key)), val]
        player.set_activity("select_items")
        check_items = False
        return render(request, self.template_name, {"player": player,
                                                    "inventory": player_inventory, "check": check_items,
                                                    "dungeon_inventory": dungeon_inventory})


def select_items(request):
    player, log, inventory = get_player(request.user)
    amount = int(request.POST["amount"])
    dungeon_inventory = inventory.get_inventory("dungeon")
    player_current_inventory = inventory.get_inventory("player")
    if len(dungeon_inventory) < inventory.max_inventory:
        if request.POST["select"][-1] == "1":
            item_id = int(request.POST["select"][:-1])
            if player_current_inventory[item_id] - amount >= 0:
                try:
                    dungeon_inventory[item_id] += amount
                    player_current_inventory[item_id] -= amount
                except:
                    dungeon_inventory[item_id] = amount
                    player_current_inventory[item_id] -= amount
            else:
                messages.error(request, "You don't have that much items.")
        else:
            item_id = int(request.POST["select"][:-1])
            if dungeon_inventory[item_id] - amount >= 0:
                try:
                    player_current_inventory[item_id] += amount
                    dungeon_inventory[item_id] -= amount
                except:
                    player_current_inventory[item_id] = amount
                    dungeon_inventory[item_id] -= amount
            else:
                messages.error(request, "You don't have that much items.")

        inventory.update_inventory(dungeon_inventory, "dungeon")
        inventory.update_inventory(player_current_inventory, "player")
    else:
        messages.error(request, "Your bag is full.")

    return redirect('qa_rpg:select')
