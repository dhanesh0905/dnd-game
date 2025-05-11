import streamlit as st
import random

CLASSES = {
    "Knight": {"HP": 30, "Attack": 7, "Defense": 5},
    "Mage": {"HP": 20, "Attack": 9, "Defense": 3},
    "Shadow": {"HP": 25, "Attack": 6, "Defense": 4},
}

ENEMIES = {
    1: [{"name": "Goblin", "HP": 10, "Attack": 4}, {"name": "Rat", "HP": 6, "Attack": 3}],
    2: [{"name": "Orc", "HP": 15, "Attack": 6}, {"name": "Giant Spider", "HP": 12, "Attack": 5}],
    3: [{"name": "Troll", "HP": 25, "Attack": 8}, {"name": "Bandit Captain", "HP": 20, "Attack": 7}],
    4: [{"name": "Wraith", "HP": 30, "Attack": 9}, {"name": "Venomous Snake", "HP": 20, "Attack": 8}],
    5: [{"name": "Warlock", "HP": 35, "Attack": 10}, {"name": "Stone Golem", "HP": 40, "Attack": 9}],
    6: [{"name": "Dread Knight", "HP": 50, "Attack": 12}, {"name": "Lich", "HP": 60, "Attack": 14}],
    7: [{"name": "Fire Elemental", "HP": 55, "Attack": 13}, {"name": "Ice Witch", "HP": 45, "Attack": 15}],
    8: [{"name": "Vampire", "HP": 65, "Attack": 16}, {"name": "Necromancer", "HP": 70, "Attack": 18}],
    9: [{"name": "Doom Bringer Lieutenant", "HP": 75, "Attack": 19}, {"name": "Chaos Beast", "HP": 80, "Attack": 20}],
    10: [{"name": "Final Guardian", "HP": 100, "Attack": 22}, {"name": "Dark Overlord Lieutenant", "HP": 90, "Attack": 21}],
}

BOSSES = {
    1: {"name": "Goblin King", "HP": 40, "Attack": 10, "Defense": 3},
    2: {"name": "Orc Warlord", "HP": 60, "Attack": 14, "Defense": 5},
    3: {"name": "Dark Dragon", "HP": 100, "Attack": 20, "Defense": 7},
    4: {"name": "Shadow Lurker", "HP": 90, "Attack": 18, "Defense": 6},
    5: {"name": "Ancient Warlock", "HP": 110, "Attack": 22, "Defense": 8},
    6: {"name": "Doom Bringer", "HP": 150, "Attack": 28, "Defense": 10},
    7: {"name": "Flame Titan", "HP": 140, "Attack": 25, "Defense": 9},
    8: {"name": "Frost Sorcerer", "HP": 160, "Attack": 27, "Defense": 11},
    9: {"name": "Chaos Champion", "HP": 180, "Attack": 30, "Defense": 12},
    10: {"name": "Dark Overlord", "HP": 220, "Attack": 35, "Defense": 15},
}

PUZZLES = {
    1: {"question": "I speak without a mouth and hear without ears. I have nobody, but I come alive with the wind. What am I?", "answer": "echo"},
    2: {"question": "The more of this there is, the less you see. What is it?", "answer": "darkness"},
    3: {"question": "I have cities, but no houses; forests, but no trees; and water, but no fish. What am I?", "answer": "map"},
    4: {"question": "What can fill a room but takes up no space?", "answer": "light"},
    5: {"question": "What has keys but can't open locks?", "answer": "piano"},
    6: {"question": "I am always hungry and will die if not fed, but whatever I touch will soon turn red. What am I?", "answer": "fire"},
    7: {"question": "I’m tall when I’m young, and I’m short when I’m old. What am I?", "answer": "candle"},
    8: {"question": "What can travel around the world while staying in the same spot?", "answer": "stamp"},
    9: {"question": "What has hands but can’t clap?", "answer": "clock"},
    10: {"question": "What is so fragile that saying its name breaks it?", "answer": "silence"},
}

FLOOR_STORY = {
    0: "In the kingdom of Eldoria, darkness looms beneath the ancient Tower of Trials. You, a brave adventurer, enter the tower seeking to restore peace and claim glory.",
    1: "Floor 1: Entrance Hall - Goblins lurk in the dim light.",
    2: "Floor 2: Creeping Depths - Orcs and spiders stalk you.",
    3: "Floor 3: Forgotten Barracks - Trolls and bandits await.",
    4: "Floor 4: Phantom Chambers - Ghostly wraiths and snakes haunt.",
    5: "Floor 5: Arcane Sanctuary - Warlocks and golems guard the halls.",
    6: "Floor 6: Dragon’s Lair - Face the Doom Bringer, the final boss.",
    7: "Floor 7: Flame Sanctum - The fearsome Flame Titan tests your courage.",
    8: "Floor 8: Frost Keep - The icy grip of the Frost Sorcerer chills your bones.",
    9: "Floor 9: Chaos Rift - The battleground of the Chaos Champion awaits.",
    10: "Floor 10: Dark Overlord's Throne - The final confrontation with the Dark Overlord.",
}

MAX_FLOOR = 10
BASE_SKILL_POINTS = 5

def init_game():
    st.session_state.update(
        player_class=None, base_hp=0, base_attack=0, base_defense=0,
        hp=0, attack=0, defense=0, floor=1,
        in_combat=False, enemy=None, enemy_hp=0,
        in_puzzle=False, puzzle_solved=False,
        message_log=[], game_over=False,
        skill_points=BASE_SKILL_POINTS, pending_skill_points=True,
        fighting_boss=False,
    )

def start_game(chosen_class):
    stats = CLASSES[chosen_class]
    st.session_state.update(
        player_class=chosen_class, base_hp=stats["HP"], base_attack=stats["Attack"], base_defense=stats["Defense"],
        hp=stats["HP"], attack=stats["Attack"], defense=stats["Defense"],
        floor=1, in_combat=False, enemy=None, enemy_hp=0,
        in_puzzle=False, puzzle_solved=False,
        message_log=[FLOOR_STORY[0], f"You chose the {chosen_class}. Your adventure begins!"],
        game_over=False, skill_points=BASE_SKILL_POINTS,
        pending_skill_points=True, fighting_boss=False,
    )

def apply_skill_points(hp_points, atk_points, def_points):
    total = hp_points + atk_points + def_points
    if total > st.session_state.skill_points:
        st.error(f"Only {st.session_state.skill_points} skill points available.")
        return False
    st.session_state.base_hp += hp_points * 5
    st.session_state.base_attack += atk_points
    st.session_state.base_defense += def_points
    st.session_state.hp = st.session_state.base_hp
    st.session_state.attack = st.session_state.base_attack
    st.session_state.defense = st.session_state.base_defense
    st.session_state.skill_points -= total
    if st.session_state.skill_points == 0:
        st.session_state.pending_skill_points = False
    return True

def encounter_enemy():
    if random.random() < 0.6:
        enemy = random.choice(ENEMIES.get(st.session_state.floor, ENEMIES[MAX_FLOOR]))
        st.session_state.enemy = enemy
        st.session_state.enemy_hp = enemy["HP"]
        st.session_state.in_combat = True
        st.session_state.message_log.append(f"A wild {enemy['name']} appears!")
        return True
    return False

def start_puzzle():
    puzzle = PUZZLES.get(st.session_state.floor)
    if puzzle:
        st.session_state.in_puzzle = True
        st.session_state.puzzle_solved = False
        st.session_state.message_log.append("You encounter a puzzle!")
    else:
        st.session_state.in_puzzle = False

def player_attack():
    if st.session_state.in_combat and not st.session_state.game_over:
        damage = max(0, st.session_state.attack - random.randint(0,3))
        st.session_state.enemy_hp -= damage
        st.session_state.message_log.append(f"You dealt {damage} damage to the {st.session_state.enemy['name']}.")
        if st.session_state.enemy_hp <= 0:
            if st.session_state.fighting_boss:
                st.session_state.message_log.append(f"You defeated the boss {st.session_state.enemy['name']}!")
                st.session_state.fighting_boss = False
                st.session_state.in_combat = False
                st.session_state.enemy = None
                st.session_state.enemy_hp = 0
                st.session_state.skill_points += BASE_SKILL_POINTS
                st.session_state.pending_skill_points = True
            else:
                st.session_state.message_log.append(f"You defeated the {st.session_state.enemy['name']}!")
                st.session_state.in_combat = False
                st.session_state.enemy = None
                st.session_state.enemy_hp = 0
            return True
        else:
            enemy_attack()
    return False