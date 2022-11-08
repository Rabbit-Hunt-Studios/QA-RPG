from abc import ABC


class Item(ABC):

    instant = False
    lingering = False

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


class PotionItem(Item):
    """Heal 20 health points instantly."""

    instant = True

    def health_modifier(self, max_health):
        return 20

    def __str__(self):
        return "Minor Potion"


class MegaPotionItem(Item):
    """Heal 50 percent of max health."""

    instant = True

    def health_modifier(self, max_health):
        return int(max_health * 0.5)

    def __str__(self):
        return "Mega Potion"


class CrossBowItem(Item):
    """Add 20 percent to escape chance."""

    lingering = True

    def escape_modifier(self, chance):
        return 0.2

    def __str__(self):
        return "Crossbow"


class SmokeBombItem(Item):
    """Ensures 100 percent escape chance."""

    lingering = True

    def escape_modifier(self, chance):
        return chance * 2

    def __str__(self):
        return "Smoke Bomb"


class ShieldItem(Item):
    """Incoming damage is is subtracted by 20 percent."""

    lingering = True

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.2)

    def __str__(self):
        return "Iron Shield"


class GreatShieldItem(Item):
    """Incoming damage is halved."""

    lingering = True

    def damage_modifier(self, incoming_damage):
        return int(incoming_damage * 0.5)

    def __str__(self):
        return "Great Shield"


class CoinBagItem(Item):
    """Coin gain is multiplied by 1.5."""

    lingering = True

    def coin_modifier(self, coin):
        return int(coin * 0.5)

    def __str__(self):
        return "Coin Bag"


class GreedyBagItem(Item):
    """Coin gain is multiplied by 3, but incoming damage is multiplied by 2."""

    lingering = True

    def coin_modifier(self, coin):
        return coin * 2

    def damage_modifier(self, incoming_damage):
        return -incoming_damage

    def __str__(self):
        return "Greedy bag"


class BloodPactItem(Item):
    """Instantly lose 15 health but gain 2 times multiplier to coin."""

    instant = True
    lingering = True

    def coin_modifier(self, coin):
        return coin

    def health_modifier(self, max_health):
        return -15

    def __str__(self):
        return "Blood Pact"


class PoisonousSmokeBombItem(Item):
    """Ensure escape chance but lose 10 health instantly."""

    instant = True
    lingering = True

    def escape_modifier(self, chance):
        return chance * 2

    def health_modifier(self, max_health):
        return -10

    def __str__(self):
        return "Poisonous Smoke Screen"


class AdrenalineItem(Item):
    """Heal 25 percent of max health but don't gain coins from current battle."""

    instant = True
    lingering = True

    def health_modifier(self, max_health):
        return int(max_health * 0.25)

    def coin_modifier(self, coin):
        return -coin

    def __str__(self):
        return "Adrenaline"


class BrokenShieldItem(Item):
    """Blocks 100 percent of incoming damage up to 30 damage if it fails 1.5 damage is applied."""

    lingering = True

    def damage_modifier(self, incoming_damage):
        if incoming_damage <= 30:
            return incoming_damage
        return -int(incoming_damage * 0.5)

    def __str__(self):
        return "Broken Shield"


class ItemCatalog:

    items = {0: PotionItem, 1: CrossBowItem, 2: ShieldItem, 3: CoinBagItem,
             10: MegaPotionItem, 11: SmokeBombItem, 12: GreatShieldItem,
             50: GreedyBagItem, 51: BloodPactItem, 52: PoisonousSmokeBombItem, 53: AdrenalineItem,
             54: BrokenShieldItem, 999: Item}

    def get_item(self, index: int):
        return self.items[index]

    def get_store_items(self):
        in_store = {}
        for key, item in self.items.items():
            if key <= 9:
                in_store[str(item)] = [key, 75]
        return in_store
