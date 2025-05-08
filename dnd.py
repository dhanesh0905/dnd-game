import random
import sys

# Starter stats for character classes
CHARACTER_CLASSES = {
    "Warrior": {
        "health": 120,
        "mana": 30,
        "strength": 15,
        "agility": 10,
        "intelligence": 5,
        "description": "Strong melee fighter."
    },
    "Mage": {
        "health": 70,
        "mana": 120,
        "strength": 5,
        "agility": 10,
        "intelligence": 18,
        "description": "Powerful spellcaster."
    },
    "Rogue": {
        "health": 90,
        "mana": 50,
        "strength": 12,
        "agility": 18,
        "intelligence": 8,
        "description": "Fast and stealthy attacker."
    }
}
class Player:
    def __init__(self, char_name):
        stats = CHARACTER_CLASSES[char_name]
        self.name = char_name
        self.health = stats["health"]
        self.mana = stats["mana"]
        self.strength = stats["strength"]
        self.agility = stats["agility"]
        self.intelligence = stats["intelligence"]
        self.description = stats["description"]
        self.current_health = self.health
        self.current_mana = self.mana

    def is_alive(self):
        return self.current_health > 0

    def basic_attack(self):
        damage = self.strength + random.randint(0, self.agility)
        return damage

    def use_ability(self):
        if self.name == "Warrior":
            cost = 10
            if self.current_mana < cost:
                return (0, "Not enough mana for Power Strike!")
            self.current_mana -= cost
            damage = self.strength * 2 + random.randint(5, 10)
            return (damage, f"Power Strike deals {damage} damage!")
        elif self.name == "Mage":
            cost = 25
            if self.current_mana < cost:
                return (0, "Not enough mana for Fireball!")
            self.current_mana -= cost
            damage = self.intelligence * 3 + random.randint(10, 15)
            return (damage, f"Fireball deals {damage} magic damage!")
        elif self.name == "Rogue":
            cost = 15
            if self.current_mana < cost:
                return (0, "Not enough mana for Backstab!")
            self.current_mana -= cost
            base_damage = self.strength + self.agility
            crit = random.random() < 0.5
            damage = base_damage * (2 if crit else 1) + random.randint(3, 7)
            if crit:
                return (damage, f"Backstab Critical! Deals {damage} damage!")
            else:
                return (damage, f"Backstab hits for {damage} damage!")
        else:
            return (0, "No ability found.")
        