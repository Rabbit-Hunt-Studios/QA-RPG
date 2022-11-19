"""Module that contains all item classes and item catalog class."""
import random
from abc import ABC


class Item(ABC):

    @property
    def description(self):
        return ""

    @property
    def effect(self):
        return ""

    def coin_modifier(self, coin):
        """Abstract method for getting money modifier."""
        return 0

    def escape_modifier(self, chance):
        """Abstract method for getting escape chance modifier."""
        return 0

    def damage_modifier(self, incoming_damage):
        """Abstract method for getting damage modifier."""
        return 0

    def health_modifier(self, max_health):
        """Abstract method for getting health modifier."""
        return 0

    def item_modifier(self, item):
        """Abstract method for getting extra items."""
        return 0


class DungeonCandyItem(Item):
    """Heal 5-10 health points instantly."""

    def health_modifier(self, max_health):
        return random.randrange(5, 11, 1)

    def __str__(self):
        return "Dungeon Candy"

    @property
    def description(self):
        return "A sweet candy favored by adventurers."

    @property
    def effect(self):
        return "Heals 5 to 10 health points instantly upon use."


class PotionItem(Item):
    """Heal 20 health points instantly."""

    def health_modifier(self, max_health):
        return 20

    def __str__(self):
        return "Minor Potion"

    @property
    def description(self):
        return "A simple healing concoction made from various herbs and monster parts."

    @property
    def effect(self):
        return "Heals 20 health points instantly upon use."


class MegaPotionItem(Item):
    """Heal 50 percent of max health."""

    def health_modifier(self, max_health):
        return int(max_health * 0.5)

    def __str__(self):
        return "Mythical Potion"

    @property
    def description(self):
        return "A potion left behind by the greatest wizard of all the lands."

    @property
    def effect(self):
        return "Heal 50 percent of max health instantly."


class CrossBowItem(Item):
    """Add 10 percent to escape chance."""

    def escape_modifier(self, chance):
        return 0.1

    def __str__(self):
        return "Crossbow"

    @property
    def description(self):
        return "Mechanical engineering at its finest, shoots straight as a die."

    @property
    def effect(self):
        return "Adds 10 percent to your escape chance."


class SmokeBombItem(Item):
    """Ensures 100 percent escape chance."""

    def escape_modifier(self, chance):
        return chance

    def __str__(self):
        return "Ninja Smoke Bomb"

    @property
    def description(self):
        return "The recipe to replicate this thick fog remains a mystery."

    @property
    def effect(self):
        return "Gain 100 percent escape chance."


class WoodenShieldItem(Item):
    """Incoming damage is subtracted by 6 damage."""

    def damage_modifier(self, incoming_damage):
        return 6

    def __str__(self):
        return "Wooden Shield"

    @property
    def description(self):
        return "Flimsy shield that looks like its about to break any time."

    @property
    def effect(self):
        return "Blocks 6 points of incoming damage."


class ShieldItem(Item):
    """Incoming damage is subtracted by 20 percent."""

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.375)

    def __str__(self):
        return "Iron Shield"

    @property
    def description(self):
        return "Sturdy, reliable, now that's a shield."

    @property
    def effect(self):
        return "Blocks 37.5 percent of damage taken."


class GreatShieldItem(Item):
    """Incoming damage is halved."""

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.75)

    def __str__(self):
        return "Aegis Shield"

    @property
    def description(self):
        return "A shield built from materials existing only in legends."

    @property
    def effect(self):
        return "Blocks 75 percent of incoming damage."


class CoinBagItem(Item):
    """Coin gain is multiplied by 2.1."""

    multiplier = 1.1

    def coin_modifier(self, coin):
        return int(coin * self.multiplier)

    def __str__(self):
        return "Coin Bag"

    @property
    def description(self):
        return "Hand crafted leather bag that holds more than you think."

    @property
    def effect(self):
        return f"Coin gain is multiplied by {1 + self.multiplier}."


class BookAlchemyItem(Item):
    f"""Coin gain is multiplied by 4."""

    multiplier = 3

    def coin_modifier(self, coin):
        return int(coin * self.multiplier)

    def __str__(self):
        return "Book of Alchemy"

    @property
    def description(self):
        return "Every imaginable forbidden magic is contained in this very book."

    @property
    def effect(self):
        return f"Coin gain is multiplied by {1 + self.multiplier}."


class AmbrosiaItem(Item):
    """Heal 30 percent instantly and 30 percent incoming damage is blocked."""

    def health_modifier(self, max_health):
        return int(max_health * 0.3)

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.3)

    def __str__(self):
        return "Ambrosia"

    @property
    def description(self):
        return "This drink is said to be procured from the Fountain of Youth."

    @property
    def effect(self):
        return "Heal 30 percent of max health instantly and blocks 30 percent of incoming damage."


class GreedyBagItem(Item):
    """Coin gain is multiplied by 3.25, but incoming damage is multiplied by 2."""

    def coin_modifier(self, coin):
        return int(coin * 2.25)

    def damage_modifier(self, incoming_damage):
        return -int(incoming_damage * 1.5)

    def __str__(self):
        return "Greedy Bag"

    @property
    def description(self):
        return "A mysterious devilish aura surrounds it."

    @property
    def effect(self):
        return "Multiplies coin gain by 3.25 times, but also multiplies damage taken by 2 times."


class BloodPactItem(Item):
    """Instantly lose 15 percent of max health, but gain 2.25 times multiplier to coin."""

    def coin_modifier(self, coin):
        return int(coin * 1.5)

    def health_modifier(self, max_health):
        return -int(max_health * 0.15)

    def __str__(self):
        return "Blood Pact"

    @property
    def description(self):
        return "Your blood is valuable to demons as coins are to you."

    @property
    def effect(self):
        return "Lose 15 percent of max health instantly, but multiplies coin gain by 2.5 times."


class PoisonousSmokeBombItem(Item):
    """Add 40 percent to escape chance but lose 15 health instantly."""

    def escape_modifier(self, chance):
        return 0.4

    def health_modifier(self, max_health):
        return -15

    def __str__(self):
        return "Poisonous Cloud"

    @property
    def description(self):
        return "Don't know who thought using poison was a good idea."

    @property
    def effect(self):
        return "Lose 15 health instantly, but adds 40 percent escape chance."


class AdrenalineItem(Item):
    """Heal 12 percent of max health but don't gain coins from current battle."""

    def health_modifier(self, max_health):
        return int(max_health * 0.12)

    def coin_modifier(self, coin):
        return -coin

    def __str__(self):
        return "Adrenaline Shot"

    @property
    def description(self):
        return "Blood rushes through your body, empowering you for a short period."

    @property
    def effect(self):
        return "Heals 12 percent of max health, but coin gains becomes zero."


class BrokenShieldItem(Item):
    """Blocks 100 percent of incoming damage up to 27 damage if it fails 1.5 damage is applied."""

    def damage_modifier(self, incoming_damage):
        if incoming_damage <= 27:
            return incoming_damage
        return -int(incoming_damage * 0.5)

    def __str__(self):
        return "Broken Shield"

    @property
    def description(self):
        return "A once legendary shield worn down to its last use."

    @property
    def effect(self):
        return "Blocks 100 percent of damage taken up to 27 damage otherwise take 50 percent extra damage."


class RuneBulwarkItem(Item):
    """Sacrifice 5 percent of max health to block 27.5 percent of incoming damage."""

    def health_modifier(self, max_health):
        return -int(max_health * 0.05)

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.275)

    def __str__(self):
        return "Rune of Bulwark"

    @property
    def description(self):
        return "An Ancient rune which is triggered with your blood."

    @property
    def effect(self):
        return "Lose 5 percent of your max health instantly, and block 27.5 percent of incoming damage."


class VialIchorItem(Item):
    """50 percent chance of healing or damaging you up to 15 percent."""

    def health_modifier(self, max_health):
        return int((random.randrange(-15, 16, 1)) * 0.01 * max_health)

    def __str__(self):
        return "Vial of Ichor"

    @property
    def description(self):
        return "A vial filled with a peculiar glowing substance, use at your own risk."

    @property
    def effect(self):
        return "Randomizes from -15 percent to 15 percent which will be added to your health."


class MermaidTearItem(Item):
    """Heal 17.5 percent of max health instantly, but incoming damage is multiplied by 1.75."""

    def health_modifier(self, max_health):
        return int(max_health * 0.175)

    def damage_modifier(self, incoming_damage):
        return -int(incoming_damage * 0.75)

    def __str__(self):
        return "Mermaid Tears"

    @property
    def description(self):
        return "Legend has it, these tears were from a grieving mother."

    @property
    def effect(self):
        return "Heal 17.5 percent of max health instantly, but gain 1.75 multiplier to incoming damage."


class GloveMidasItem(Item):
    """Ensures you get a cursed item and times it by 2."""

    def item_modifier(self, item):
        return 1

    def __str__(self):
        return "Glove of Midas"

    @property
    def description(self):
        return "A glove enchanted with replication magic."

    @property
    def effect(self):
        return "Ensures that 2 items of the same kind drop from monster."


class ItemCatalog:
    """Dataclass containing all items and their corresponding index."""

    __ITEMS = {0: DungeonCandyItem(), 1: WoodenShieldItem(),
               6: PotionItem(), 7: CrossBowItem(), 8: ShieldItem(), 9: CoinBagItem(),

               10: MegaPotionItem(), 11: SmokeBombItem(), 12: GreatShieldItem(), 13: AmbrosiaItem(),
               14: BookAlchemyItem(), 15: GloveMidasItem(),

               50: GreedyBagItem(), 51: BloodPactItem(), 52: PoisonousSmokeBombItem(), 53: AdrenalineItem(),
               54: BrokenShieldItem(), 55: VialIchorItem(), 56: RuneBulwarkItem(), 57: MermaidTearItem(),

               999: Item()}

    __STORE_30 = [0, 1, 9]
    __STORE_80 = [6, 7, 8]

    def get_item(self, index: int):
        """Return item to the corresponding index."""
        return self.__ITEMS[index]
        
    def get_store_items(self):
        in_store = {}
        for index in self.__STORE_30:
            item = self.get_item(index)
            in_store[str(item)] = [index, 30, item.description, item.effect]
        for index in self.__STORE_80:
            item = self.get_item(index)
            in_store[str(item)] = [index, 80, item.description, item.effect]
        return in_store

    def get_chest_items(self):
        return [key for key in self.__ITEMS.keys() if (10 <= key < 20)]

    def get_cursed_items(self):
        return [key for key in self.__ITEMS.keys() if (50 <= key < 60)]

