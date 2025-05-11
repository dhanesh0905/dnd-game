import streamlit as st
import random

# Classes with detailed stats and descriptions
CLASSES = {
    "Knight": {
        "health": 100,
        "mana": 20,
        "strength": 15,
        "agility": 8,
        "intelligence": 5,
        "description": "A strong melee fighter with high health and strength."
    },
    "Mage": {
        "health": 60,
        "mana": 100,
        "strength": 5,
        "agility": 10,
        "intelligence": 18,
        "description": "A spellcaster with powerful magic but low health."
    },
    "Shadow": {
        "health": 80,
        "mana": 40,
        "strength": 10,
        "agility": 18,
        "intelligence": 7,
        "description": "A stealthy assassin with high agility and balanced stats."
    },
}

# Enemies and bosses with simplified stats
ENEMIES = {
    1: [{"name": "Goblin", "health": 40, "strength": 10, "agility": 5}],
    2: [{"name": "Orc", "health": 60, "strength": 14, "agility": 7}],
    3: [{"name": "Troll", "health": 80, "strength": 18, "agility": 6}],
    4: [{"name": "Wraith", "health": 90, "strength": 20, "agility": 12}],
    5: [{"name": "Warlock", "health": 100, "strength": 22, "agility": 8}],
    6: [{"name": "Dread Knight", "health": 110, "strength": 25, "agility": 10}],
}

BOSSES = {
    1: {"name": "Goblin King", "health": 100, "strength": 20, "agility": 10, "description": "The brutal Goblin King."},
    2: {"name": "Orc Warlord", "health": 140, "strength": 28, "agility": 12, "description": "The fearsome Orc commander."},
    3: {"name": "Dark Dragon", "health": 180, "strength": 35, "agility": 15, "description": "A mighty dragon shrouded in darkness."},
    4: {"name": "Shadow Lurker", "health": 160, "strength": 30, "agility": 20, "description": "A deadly phantom of the shadows."},
    5: {"name": "Ancient Warlock", "health": 190, "strength": 32, "agility": 14, "description": "Master of forbidden magic."},
    6: {"name": "Doom Bringer", "health": 220, "strength": 40, "agility": 18, "description": "Harbinger of the world's end."},
}

PUZZLES = {
    1: {"question": "I speak without a mouth and hear without ears. What am I?", "answer": "echo"},
    2: {"question": "The more of this there is, the less you see. What is it?", "answer": "darkness"},
    3: {"question": "I have cities, but no houses; forests, but no trees; and water, but no fish. What am I?", "answer": "map"},
    4: {"question": "What can fill a room but takes up no space?", "answer": "light"},
    5: {"question": "What has keys but can't open locks?", "answer": "piano"},
    6: {"question": "I am always hungry and will die if not fed, but whatever I touch will soon turn red. What am I?", "answer": "fire"},}

FLOOR_STORY = {
    0: "In the kingdom of Eldoria, darkness looms beneath the ancient Tower of Trials. You, a brave adventurer, enter the tower seeking to restore peace and claim glory.",
    1: "Floor 1: Entrance Hall - Goblins lurk in the dim light.",
    2: "Floor 2: Creeping Depths - Orcs and spiders stalk you.",
    3: "Floor 3: Forgotten Barracks - Trolls and bandits await.",
    4: "Floor 4: Phantom Chambers - Ghostly wraiths and snakes haunt.",
    5: "Floor 5: Arcane Sanctuary - Warlocks and golems guard the halls.",
    6: "Floor 6: Dragon’s Lair - Face the Doom Bringer, the final boss.",}

MAX_FLOOR = 6
BASE_SKILL_POINTS = 5

def init_game():
    st.session_state.update(
        player_class=None,
        health=0,
        mana=0,
        strength=0,
        agility=0,
        intelligence=0,
        max_health=0,
        max_mana=0,
        floor=1,
        in_combat=False,
        enemy=None,
        enemy_health=0,
        in_puzzle=False,
        puzzle_solved=False,
        message_log=[],
        game_over=False,
        skill_points=BASE_SKILL_POINTS,
        pending_skill_points=True,
        fighting_boss=False,
    )
    def start_game(chosen_class):
        
       stats = CLASSES[chosen_class]
    st.session_state.update(
        player_class=chosen_class,
        health=stats["health"],
        max_health=stats["health"],
        mana=stats["mana"],
        max_mana=stats["mana"],
        strength=stats["strength"],
        agility=stats["agility"],
        intelligence=stats["intelligence"],
        floor=1,
        in_combat=False,
        enemy=None,
        enemy_health=0,
        in_puzzle=False,
        puzzle_solved=False,
        message_log=[FLOOR_STORY[0], f"You chose the {chosen_class}. {stats['description']} Your adventure begins!"],
        game_over=False,
        skill_points=BASE_SKILL_POINTS,
        pending_skill_points=True,
        fighting_boss=False,
    )

def apply_skill_points(hp_points, mana_points, str_points, agi_points, int_points):
    total = hp_points + mana_points + str_points + agi_points + int_points
    if total > st.session_state.skill_points:
        st.error(f"Only {st.session_state.skill_points} skill points available.")
        return False
    st.session_state.max_health += hp_points * 10
    st.session_state.max_mana += mana_points * 10
    st.session_state.strength += str_points
    st.session_state.agility += agi_points
    st.session_state.intelligence += int_points
    # Heal player to new max values when points are applied
    st.session_state.health = st.session_state.max_health
    st.session_state.mana = st.session_state.max_mana
    st.session_state.skill_points -= total
    if st.session_state.skill_points == 0:
        st.session_state.pending_skill_points = False
    return True

def encounter_enemy():
    if random.random() < 0.6:
        enemy = random.choice(ENEMIES.get(st.session_state.floor, ENEMIES[MAX_FLOOR]))
        st.session_state.enemy = enemy
        st.session_state.enemy_health = enemy["health"]
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
        base_damage = st.session_state.strength
        # Critical hit chance based on agility/100
        crit_chance = min(0.3, st.session_state.agility / 100)
        crit = random.random() < crit_chance
        damage = max(0, base_damage + (base_damage // 2 if crit else 0) - random.randint(0, 3))
        st.session_state.enemy_health -= damage
        if crit:
            st.session_state.message_log.append(f"Critical hit! You deal {damage} damage to the {st.session_state.enemy['name']}.")
        else:
            st.session_state.message_log.append(f"You deal {damage} damage to the {st.session_state.enemy['name']}.")
        if st.session_state.enemy_health <= 0:
            if st.session_state.fighting_boss:
                st.session_state.message_log.append(f"You defeated the boss {st.session_state.enemy['name']}!")
                st.session_state.fighting_boss = False
                st.session_state.in_combat = False
                st.session_state.enemy = None
                st.session_state.enemy_health = 0
                st.session_state.skill_points += BASE_SKILL_POINTS
                st.session_state.pending_skill_points = True
            else:
                st.session_state.message_log.append(f"You defeated the {st.session_state.enemy['name']}!")
                st.session_state.in_combat = False
                st.session_state.enemy = None
                st.session_state.enemy_health = 0
            return True
        else:
            enemy_attack()
    return False