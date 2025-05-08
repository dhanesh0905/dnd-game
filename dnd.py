import random

# Starter stats for character classes
CHARACTER_CLASSES = {
    "knight": {
        "health": 120,
        "mana": 30,
        "strength": 15,
        "agility": 10,
        "intelligence": 5,
        "description": "Strong melee fighter."
    },
    "magierin": {
        "health": 70,
        "mana": 120,
        "strength": 5,
        "agility": 10,
        "intelligence": 18,
        "description": "Powerful spellcaster."
    },
    "the shadow": {
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
class Enemy:
    def __init__(self, name, health, strength, description):
        self.name = name
        self.health = health
        self.strength = strength
        self.description = description

    def is_alive(self):
        return self.health > 0

    def attack(self):
        damage = self.strength + random.randint(0, 5)
        return damage

def random_enemy():
    enemy_types = [
        Enemy("Goblin", 100, 12, "A sneaky and quick foe."),
        Enemy("Orc", 140, 18, "A brutish and powerful warrior."),
        Enemy("Skeleton", 80, 10, "An undead soldier risen from the grave."),
    ]
    return random.choice(enemy_types)

FLOORS = [
    {"name": "Goblin Lair", "enemy": {"name":"Goblin", "health":100, "strength":12, "description":"A sneaky and quick foe."},
     "puzzle": {"question": "What number comes next in the sequence? 2, 3, 5, 7, 11, ?", "answer": "13"}},
    {"name": "Orc Camp", "enemy": {"name":"Orc", "health":140, "strength":18, "description":"A brutish and powerful warrior."},
     "puzzle": {"question": "I speak without a mouth and hear without ears. What am I?", "answer": "echo"}},
    {"name": "Skeleton Crypt", "enemy": {"name":"Skeleton", "health":80, "strength":10, "description":"An undead soldier risen from the grave."},
     "puzzle": {"question": "What has to be broken before you can use it?", "answer": "egg"}},
    {"name": "Spider Nest", "enemy": {"name":"Giant Spider", "health":110, "strength":14, "description":"A venomous spider lurking in shadows."},
     "puzzle": {"question": "What can fill a room but takes up no space?", "answer": "light"}},
    {"name": "Bandit Hideout", "enemy": {"name":"Bandit", "health":130, "strength":16, "description":"A ruthless human thug."},
     "puzzle": {"question": "What has keys but can't open locks?", "answer": "piano"}},
    {"name": "Dark Mage Tower", "enemy": {"name":"Dark Mage", "health":90, "strength":20, "description":"A master of dark magic."},
     "puzzle": {"question": "What runs around a yard without moving?", "answer": "fence"}},
    {"name": "Wraith's Haunt", "enemy": {"name":"Wraith", "health":150, "strength":15, "description":"A ghostly and ethereal foe."},
     "puzzle": {"question": "I’m tall when I’m young, and I’m short when I’m old. What am I?", "answer": "candle"}},
    {"name": "Troll Bridge", "enemy": {"name":"Troll", "health":200, "strength":22, "description":"A huge and terrifying brute."},
     "puzzle": {"question": "What gets wetter as it dries?", "answer": "towel"}},
    {"name": "Dragon's Cave", "enemy": {"name":"Young Dragon", "health":250, "strength":30, "description":"A fierce dragon with fiery breath."},
     "puzzle": {"question": "What belongs to you but is used by others more than you?", "answer": "your name"}},
    {"name": "Demon Gate", "enemy": {"name":"Demon Lord", "health":800, "strength":45, "description":"The ultimate evil to defeat."},
     "puzzle": {"question": "The more of this there is, the less you see. What is it?", "answer": "darkness"}},
]