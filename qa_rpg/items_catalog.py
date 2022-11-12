import random
from abc import ABC
from dataclasses import dataclass


class Item(ABC):

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

    


class PotionItem(Item):
    """Heal 20 health points instantly."""

    def health_modifier(self, max_health):
        return 20

    def __str__(self):
        return "Minor Potion"


class MegaPotionItem(Item):
    """Heal 50 percent of max health."""

    def health_modifier(self, max_health):
        return int(max_health * 0.5)

    def __str__(self):
        return "Mythical Potion"


class CrossBowItem(Item):
    """Add 20 percent to escape chance."""

    def escape_modifier(self, chance):
        return 0.1

    def __str__(self):
        return "Crossbow"


class SmokeBombItem(Item):
    """Ensures 95 percent escape chance."""

    def escape_modifier(self, chance):
        return chance - 0.05

    def __str__(self):
        return "Ninja Smoke Bomb"


class WoodenShieldItem(Item):
    """Incoming damage is subtracted by 6 damage."""

    def damage_modifier(self, incoming_damage):
        return 6

    def __str__(self):
        return "Wooden Shield"


class ShieldItem(Item):
    """Incoming damage is subtracted by 20 percent."""

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.2)

    def __str__(self):
        return "Iron Shield"


class GreatShieldItem(Item):
    """Incoming damage is halved."""

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.5)

    def __str__(self):
        return "Aegis Shield"


class CoinBagItem(Item):
    """Coin gain is multiplied by 1.5."""

    def coin_modifier(self, coin):
        return int(coin * 0.5)

    def __str__(self):
        return "Coin Bag"


class BookAlchemyItem(Item):
    """Coin gain is multiplied by 2.5."""

    def coin_modifier(self, coin):
        return int(coin * 1.5)

    def __str__(self):
        return "Book of Alchemy"


class AmbrosiaItem(Item):
    """Heal 25 percent instantly and 25 percent incoming damage is blocked."""

    def health_modifier(self, max_health):
        return int(max_health * 0.25)

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.25)

    def __str__(self):
        return "Ambrosia"


class GreedyBagItem(Item):
    """Coin gain is multiplied by 3, but incoming damage is multiplied by 2."""

    def coin_modifier(self, coin):
        return coin * 2

    def damage_modifier(self, incoming_damage):
        return -incoming_damage

    def __str__(self):
        return "Greedy Bag"


class BloodPactItem(Item):
    """Instantly lose 15 percent of max health, but gain 2 times multiplier to coin."""

    def coin_modifier(self, coin):
        return coin

    def health_modifier(self, max_health):
        return -int(max_health * 0.15)

    def __str__(self):
        return "Blood Pact"


class PoisonousSmokeBombItem(Item):
    """Add 40 percent to escape chance but lose 10 percent max health instantly."""

    def escape_modifier(self, chance):
        return 0.3

    def health_modifier(self, max_health):
        return -int(max_health * 0.08)

    def __str__(self):
        return "Poisonous Cloud"


class AdrenalineItem(Item):
    """Heal 12 percent of max health but don't gain coins from current battle."""

    def health_modifier(self, max_health):
        return int(max_health * 0.12)

    def coin_modifier(self, coin):
        return -coin

    def __str__(self):
        return "Adrenaline Shot"


class BrokenShieldItem(Item):
    """Blocks 100 percent of incoming damage up to 27 damage if it fails 1.5 damage is applied."""

    def damage_modifier(self, incoming_damage):
        if incoming_damage <= 27:
            return incoming_damage
        return -int(incoming_damage * 0.5)

    def __str__(self):
        return "Broken Shield"


class RuneBulwarkItem(Item):
    """Sacrifice 5 percent of max health to block 27.5 percent of incoming damage."""

    def health_modifier(self, max_health):
        return -int(max_health * 0.05)

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.275)

    def __str__(self):
        return "Rune of Bulwark"
    
    

class VialIchorItem(Item):
    """50 percent chance of healing or damaging you up to 10 percent."""

    def health_modifier(self, max_health):
        return int((random.randrange(-10, 10, 1)) * 0.01 * max_health)

    def __str__(self):
        return "Vial of Ichor"


class MermaidTearItem(Item):
    """Heal 17.5 percent of max health instantly, but incoming damage is multiplied by 1.75."""

    def health_modifier(self, max_health):
        return int(max_health * 0.175)

    def damage_modifier(self, incoming_damage):
        return -int(incoming_damage * 0.75)

    def __str__(self):
        return "Mermaid Tears"


class GloveMidasItem(Item):
    """Ensures you get a cursed item and times it by 2."""

    def item_modifier(self, item):
        return 1

    def __str__(self):
        return "Glove of Midas"


@dataclass(init=False)
class ItemCatalog:

    ITEMS = {0: DungeonCandyItem(), 1: WoodenShieldItem(),
             6: PotionItem(), 7: CrossBowItem(), 8: ShieldItem(), 9: CoinBagItem(),

             10: MegaPotionItem(), 11: SmokeBombItem(), 12: GreatShieldItem(), 13: AmbrosiaItem(),
             14: BookAlchemyItem(), 15: GloveMidasItem(),

             50: GreedyBagItem(), 51: BloodPactItem(), 52: PoisonousSmokeBombItem(), 53: AdrenalineItem(),
             54: BrokenShieldItem(), 55: VialIchorItem(), 56: RuneBulwarkItem(), 57: MermaidTearItem(),

             999: Item()}
    
    DESCRIPTION = {0: "Heals between 5 to 10 health points instantly upon use.", 1: "Blocks 6 damage of incoming damage.",
                    6: "Heals 20 health points instantly upon use.", 7: "Increase your chance of escape by 10 percents.", 
                    8: "Blocks 20 percent of damage taken.", 9: "Adds 50 percent of bonus of coin gained.",
                    10: "Heal 50 percent of max health instantly.", 11: "Gain 100 percent escape chance.", 12: "Blocks 50 percent of incoming damage.", 
                    13: "Heal 25 percent of max health instantly and blocks 25 percent of incoming damage.", 14: "Coin gain is multiplied by 2.5.", 
                    15: "Ensures that 2 items of the same kind drop from monster.",

                    50: "Multiplies coin gain by 3 times, but also multiplies damage taken by 2 times", 51: "Lose 15 percent of max health instantly, but multiplies coin gain by 2 times.", 
                    52: "Lose 10 percent of max health instantly, but adds 30 percent escape chance.", 53: "Heals 12 percent of max health, but coin gains becomes zero.",
                    54: " Blocks 100 percent of damage taken up to 27 damage otherwise take 50 percent extra damage.", 55: "Randomizes a percentage from negative 10 percent to positive 10 percent which will be added to your health.", 
                    56: "Lose 5 percent of your max health instantly, and block 27.5 percent of incoming damage.", 57: " Heal 17.5 percent of max health instantly, but gain 1.75 multiplier to incoming damage.",}

    def get_item(self, index: int):
        return self.ITEMS[index]

    def get_desciption(self, index: int):
        return self.DESCRIPTION[index]
        
    def get_store_items(self):
        in_store = {}
        for key, item in self.ITEMS.items():
            for keys, desc in self.DESCRIPTION.items():
                if key <= 5:
                    if key == keys:
                        in_store[str(item)] = [key, desc, 30]
                elif key <= 9:
                    if key == keys:
                        in_store[str(item)] = [key, desc, 75]
        return in_store

    def get_chest_items(self):
        return [key for key in self.ITEMS.keys() if (10 <= key < 20)]

    def get_cursed_items(self):
        return [key for key in self.ITEMS.keys() if (50 <= key < 60)]

