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
