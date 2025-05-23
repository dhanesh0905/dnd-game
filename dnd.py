import streamlit as st
import random

CLASSES = {
    "Knight": {
        "image_url": "https://i.pinimg.com/474x/6d/7d/b5/6d7db587491ddc0c8fde2b7040606347.jpg",  
        "health": 100,
        "mana": 20,
        "strength": 15,
        "agility": 8,
        "description": "A strong melee fighter with high health and strength.",
        "skills": {
            "Shield Bash": {"cost": 15, "damage_mult": 1.5},
            "Whirlwind": {"cost": 25, "damage_mult": 2.0}
        }
    },
    "Mage": {
        "image_url": "https://i.pinimg.com/736x/c1/e5/fd/c1e5fd12cc32f64ba8284b30c6e57de9.jpg",  
        "health": 60,
        "mana": 100,
        "strength": 5,
        "agility": 10,
        "description": "A spellcaster with powerful magic but low health.",
        "skills": {
            "Firestorm": {"cost": 30, "damage_mult": 2.5},
            "Ice Prison": {"cost": 25, "damage_mult": 1.8}
        }
    },
    "Shadow": {
        "image_url": "data:image/jpeg;base64,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", 
        "health": 80,
        "mana": 40,
        "strength": 10,
        "agility": 18,
        "description": "A stealthy assassin with high agility and balanced stats.",
        "skills": {
            "Backstab": {"cost": 20, "damage_mult": 2.2},
            "Poison Dart": {"cost": 15, "damage_mult": 1.5}
        }
    },
}


ENEMIES = {
    1: [{"name": "Goblin", "health": 40, "strength": 10, "agility": 5}],
    2: [{"name": "Orc", "health": 60, "strength": 14, "agility": 7}],
    3: [{"name": "Troll", "health": 80, "strength": 18, "agility": 6}],
    4: [{"name": "Wraith", "health": 90, "strength": 20, "agility": 12}],
    5: [{"name": "Warlock", "health": 100, "strength": 22, "agility": 8}],
    6: [{"name": "Dread Knight", "health": 110, "strength": 25, "agility": 10}],
    7: [{"name": "Fire Elemental", "health": 130, "strength": 28, "agility": 10}],
    8: [{"name": "Ice Golem", "health": 150, "strength": 32, "agility": 8}],
    9: [{"name": "Necromancer", "health": 120, "strength": 35, "agility": 15}],
    10: [{"name": "Hellhound", "health": 160, "strength": 38, "agility": 18}],
}

BOSSES = {
    1: {"name": "Goblin King", "health": 100, "strength": 20, "agility": 10, "description": "The brutal Goblin King."},
    2: {"name": "Orc Warlord", "health": 140, "strength": 28, "agility": 12, "description": "The fearsome Orc commander."},
    3: {"name": "Dark Dragon", "health": 180, "strength": 35, "agility": 15, "description": "A mighty dragon shrouded in darkness."},
    4: {"name": "Shadow Lurker", "health": 160, "strength": 30, "agility": 20, "description": "A deadly phantom of the shadows."},
    5: {"name": "Ancient Warlock", "health": 190, "strength": 32, "agility": 14, "description": "Master of forbidden magic."},
    6: {"name": "Doom Bringer", "health": 220, "strength": 40, "agility": 18, "description": "Harbinger of the world's end."},
    7: {"name": "Phoenix King", "health": 240, "strength": 45, "agility": 22, "description": "Ruler of the fiery realms."},
    8: {"name": "Frost Titan", "health": 260, "strength": 50, "agility": 18, "description": "Towering giant of eternal ice."},
    9: {"name": "Lich King", "health": 280, "strength": 55, "agility": 25, "description": "Undead monarch of the damned."},
    10: {"name": "Demon Lord", "health": 300, "strength": 60, "agility": 30, "description": "The supreme ruler of the abyss."},
}

PUZZLES = {
    1: {"question": "I speak without a mouth and hear without ears. What am I?", "answer": "echo"},
    2: {"question": "The more of this there is, the less you see. What is it?", "answer": "darkness"},
    3: {"question": "I have cities, but no houses; forests, but no trees; and water, but no fish. What am I?", "answer": "map"},
    4: {"question": "What can fill a room but takes up no space?", "answer": "light"},
    5: {"question": "What has keys but can't open locks?", "answer": "piano"},
    6: {"question": "I am always hungry and will die if not fed, but whatever I touch will soon turn red. What am I?", "answer": "fire"},
     7: {"question": "I follow you all day and mimic your moves, but I vanish in darkness. What am I?", "answer": "shadow"},
    8: {"question": "What has a heart that doesn't beat?", "answer": "artichoke"},
    9: {"question": "What can run but never walks, has a mouth but never talks?", "answer": "river"},
    10: {"question": "What is always in front of you but can't be seen?", "answer": "future"},
}

FLOOR_STORY = {
    0: "In the kingdom of Eldoria, darkness looms beneath the ancient Tower of Trials. You, a brave adventurer, enter the tower seeking to restore peace and claim glory.",
    1: "Floor 1: Entrance Hall - Goblins lurk in the dim light.",
    2: "Floor 2: Creeping Depths - Orcs and spiders stalk you.",
    3: "Floor 3: Forgotten Barracks - Trolls and bandits await.",
    4: "Floor 4: Phantom Chambers - Ghostly wraiths and snakes haunt.",
    5: "Floor 5: Arcane Sanctuary - Warlocks and golems guard the halls.",
    6: "Floor 6: Dragon's Lair - Face the Doom Bringer, the final boss.",
    7: "Floor 7: Molten Core - Lava flows and fire elementals surge.",
    8: "Floor 8: Frozen Abyss - Treacherous ice and frost titans dominate.",
    9: "Floor 9: Crypt of Despair - Undead and necromancers lurk.",
    10: "Floor 10: Throne of Chaos - Confront the Demon Lord, ruler of the abyss.",
}

MAX_FLOOR = 10
BASE_SKILL_POINTS = 5

def init_game():
    st.session_state.update(
        player_class=None,
        health=0,
        mana=0,
        strength=0,
        agility=0,
        max_health=0,
        max_mana=0,
        floor=0,
        in_combat=False,
        enemy=None,
        enemy_health=0,
        in_puzzle=False,
        puzzle_solved=False,
        message_log=[FLOOR_STORY[0]],
        game_over=False,
        skill_points=0,
        pending_skill_points=False,
        fighting_boss=False,
        solved_puzzles=set(),  
    )

def start_game(chosen_class):
    stats = CLASSES[chosen_class]
    st.session_state.update (
        player_class=chosen_class,
        player_image=stats["image_url"],  # Add image to session state
        health=stats["health"],
        max_health=stats["health"],
        mana=stats["mana"],
        max_mana=stats["mana"],
        strength=stats["strength"],
        agility=stats["agility"],
        floor=1,
        in_combat=False,
        enemy=None,
        enemy_health=0,
        in_puzzle=False,
        puzzle_solved=False,
        message_log=[FLOOR_STORY[1], f"You chose the {chosen_class}. {stats['description']} Your adventure begins!"],
        game_over=False,
        skill_points=0,
        pending_skill_points=False,
        fighting_boss=False,
        solved_puzzles=set(),  
    )

def apply_skill_points(hp_points, mana_points, str_points, agi_points):
    total = hp_points + mana_points + str_points + agi_points
    if total > st.session_state.skill_points:
        st.error(f"Only {st.session_state.skill_points} skill points available.")
        return False
    st.session_state.max_health += hp_points * 10
    st.session_state.max_mana += mana_points * 10
    st.session_state.strength += str_points
    st.session_state.agility += agi_points
    st.session_state.health = st.session_state.max_health
    st.session_state.mana = st.session_state.max_mana
    st.session_state.skill_points -= total
    if st.session_state.skill_points == 0:
        st.session_state.pending_skill_points = False
    return True

def encounter_enemy():
    if random.random() < 0.6:
        enemy_list = ENEMIES.get(st.session_state.floor)
        if enemy_list:
            enemy = random.choice(enemy_list)
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
def player_attack(skill=None):
    if st.session_state.in_combat and not st.session_state.game_over:
        if skill:
            skill_info = CLASSES[st.session_state.player_class]["skills"][skill]
            base_damage = int(st.session_state.strength * skill_info["damage_mult"])
            mana_cost = skill_info["cost"]
            if st.session_state.mana < mana_cost:
                st.session_state.message_log.append(f"Not enough mana for {skill}!")
                return
            st.session_state.mana -= mana_cost
        else:
            base_damage = st.session_state.strength
            mana_cost = 0

        crit_chance = min(0.3, st.session_state.agility / 100)
        crit = random.random() < crit_chance
        damage = max(0, base_damage + (base_damage // 2 if crit else 0) - random.randint(0, 3))
        
        st.session_state.enemy_health -= damage
        msg = f"You use {skill} and deal {damage} damage!" if skill else f"You deal {damage} damage"
        if crit:
            msg += " (Critical hit!)"
        st.session_state.message_log.append(msg)

        if st.session_state.enemy_health <= 0:
            handle_victory()
        else:
            enemy_attack()
def handle_victory():
    if st.session_state.fighting_boss:
        st.session_state.message_log.append(f"You defeated the boss {st.session_state.enemy['name']}!")
        st.session_state.skill_points += BASE_SKILL_POINTS * 2
    else:
        st.session_state.message_log.append(f"You defeated the {st.session_state.enemy['name']}!")
        st.session_state.skill_points += BASE_SKILL_POINTS
    
    st.session_state.pending_skill_points = True
    st.session_state.in_combat = False
    st.session_state.enemy = None
    st.session_state.enemy_health = 0
    st.session_state.fighting_boss = False
    
    if st.session_state.floor == MAX_FLOOR:
        st.session_state.game_over = True
        st.session_state.message_log.append("You've conquered the Tower of Trials! Legendary!")
    else:
        next_floor()

def player_attack():
    if st.session_state.in_combat and not st.session_state.game_over:
        base_damage = st.session_state.strength
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
                next_floor()
            else:
                st.session_state.message_log.append(f"You defeated the {st.session_state.enemy['name']}!")
                st.session_state.in_combat = False
                st.session_state.enemy = None
                st.session_state.enemy_health = 0
                st.session_state.skill_points += BASE_SKILL_POINTS
                st.session_state.pending_skill_points = True
            return True
        else:
            enemy_attack()
    return False

def enemy_attack():
    if st.session_state.in_combat and not st.session_state.game_over and st.session_state.enemy:
        if st.session_state.fighting_boss:
            enemy_power = BOSSES[st.session_state.floor]["strength"]
            enemy_agility = BOSSES[st.session_state.floor]["agility"]
        else:
            enemy_power = st.session_state.enemy.get("strength", 5)
            enemy_agility = st.session_state.enemy.get("agility", 5)
        evasion_chance = max(0.05, (st.session_state.agility - enemy_agility) / 100)
        if random.random() < evasion_chance:
            st.session_state.message_log.append("You evaded the enemy's attack!")
            return
        damage = max(0, enemy_power - (st.session_state.agility // 3))
        st.session_state.health -= damage
        st.session_state.message_log.append(f"Enemy hits you for {damage} damage.")
        if st.session_state.health <= 0:
            st.session_state.health = 0
            st.session_state.game_over = True
            st.session_state.message_log.append("You died. Game over.")

def solve_puzzle(answer):
    if st.session_state.in_puzzle and st.session_state.floor in PUZZLES:
        correct = PUZZLES[st.session_state.floor]["answer"]
        if answer.strip().lower() == correct:
            st.session_state.solved_puzzles.add(st.session_state.floor)
            st.session_state.puzzle_solved = True
            st.session_state.in_puzzle = False
            st.session_state.message_log.append("Puzzle solved! You may proceed.")
            st.session_state.skill_points += BASE_SKILL_POINTS
            st.session_state.pending_skill_points = True
        else:
            st.session_state.message_log.append("Wrong answer, try again.")

def start_boss():
    if st.session_state.floor in BOSSES:
        boss = BOSSES[st.session_state.floor]
        st.session_state.fighting_boss = True
        st.session_state.in_combat = True
        st.session_state.enemy = boss
        st.session_state.enemy_health = boss["health"]
        st.session_state.message_log.append(f"Boss {boss['name']} appears! {boss.get('description','')}")

def next_floor():
    if st.session_state.floor < MAX_FLOOR:
        st.session_state.floor += 1
        st.session_state.message_log.append(f"You advance to floor {st.session_state.floor}.")
        st.session_state.in_combat = False
        st.session_state.enemy = None
        st.session_state.enemy_health = 0
        st.session_state.in_puzzle = False
        st.session_state.puzzle_solved = False
        st.session_state.fighting_boss = False
        if st.session_state.floor in FLOOR_STORY:
            st.session_state.message_log.append(FLOOR_STORY[st.session_state.floor])
    else:
        st.session_state.message_log.append("You have reached the top of the tower!")
        st.session_state.game_over = True

def try_encounter():
    if st.session_state.floor > MAX_FLOOR:
        st.session_state.message_log.append("You conquered all floors! You win!")
        st.session_state.game_over = True
        return
    if not st.session_state.in_combat and not st.session_state.in_puzzle:
        if st.session_state.floor % 3 == 0:
            start_boss()
        else:
            if st.session_state.floor not in st.session_state.solved_puzzles:
                start_puzzle()
            else:
                if random.random() < 0.6:
                    encounter_enemy()
                else:
                    st.session_state.message_log.append("You find nothing but dust...")

def cast_spell():
    if st.session_state.in_combat and not st.session_state.game_over:
        if st.session_state.mana >= 20:
            st.session_state.mana -= 20
            base_damage = st.session_state.strength + 10
            damage = max(0, base_damage - random.randint(0, 5))
            st.session_state.enemy_health -= damage
            st.session_state.message_log.append(f"You cast a spell dealing {damage} damage to the {st.session_state.enemy['name']}!")
            if st.session_state.enemy_health <= 0:
                if st.session_state.fighting_boss:
                    st.session_state.message_log.append(f"You defeated the boss {st.session_state.enemy['name']}!")
                    st.session_state.fighting_boss = False
                    st.session_state.in_combat = False
                    st.session_state.enemy = None
                    st.session_state.enemy_health = 0
                    st.session_state.skill_points += BASE_SKILL_POINTS
                    st.session_state.pending_skill_points = True
                    next_floor()
                else:
                    st.session_state.message_log.append(f"You defeated the {st.session_state.enemy['name']}!")
                    st.session_state.in_combat = False
                    st.session_state.enemy = None
                    st.session_state.enemy_health = 0
                    st.session_state.skill_points += BASE_SKILL_POINTS
                    st.session_state.pending_skill_points = True
            else:
                enemy_attack()
        else:
            st.session_state.message_log.append("Not enough mana to cast a spell!")

def rest():
    if not st.session_state.in_combat and not st.session_state.in_puzzle:
        heal_amount = min(30, st.session_state.max_health - st.session_state.health)
        mana_amount = min(30, st.session_state.max_mana - st.session_state.mana)
        st.session_state.health += heal_amount
        st.session_state.mana += mana_amount
        st.session_state.message_log.append(f"You rest and recover {heal_amount} HP and {mana_amount} mana.")
        try_encounter()

st.set_page_config(page_title="Simple DnD with Stats", layout="centered")
st.title("🛡 Simple DnD Game - Stats in Combat")

if "player_class" not in st.session_state:
    init_game()

if not st.session_state.player_class:
    st.header("Choose Your Starter Class")
    cols = st.columns(3)
    for i, (c, info) in enumerate(CLASSES.items()):
        with cols[i]:
            st.subheader(c)
            st.image(info["image_url"], width=200)  # Add class image
            st.write(info["description"])
            st.write(f"Health: {info['health']}")
            st.write(f"Mana: {info['mana']}")
            st.write(f"Strength: {info['strength']}")
            st.write(f"Agility: {info['agility']}")
            if st.button(f"Select {c}"):
                start_game(c)

else:
    st.sidebar.header(f"Status - Floor {st.session_state.floor}")
    st.sidebar.image(st.session_state.player_image, width=200)
    st.sidebar.write(f"Class: {st.session_state.player_class}")
    st.sidebar.header(f"Status - Floor {st.session_state.floor}")
    st.sidebar.write(f"Class: {st.session_state.player_class}")
    st.sidebar.write(f"❤ Health: {st.session_state.health}/{st.session_state.max_health}")
    st.sidebar.write(f"🔵 Mana: {st.session_state.mana}/{st.session_state.max_mana}")
    st.sidebar.write(f"💪 Strength: {st.session_state.strength}")
    st.sidebar.write(f"🤸 Agility: {st.session_state.agility}")
    st.sidebar.write(f"Skill Points: {st.session_state.skill_points}")

    if st.session_state.game_over:
        st.error("💀 You died! Game Over." if st.session_state.health <= 0 else "🎉 You conquered all floors! You win!")
        if st.button("Restart"):
            init_game()
    else:
        st.subheader("Game Log")
        for msg in reversed(st.session_state.message_log[-10:]):
            st.write(msg)

        if st.session_state.pending_skill_points and st.session_state.skill_points > 0:
            st.subheader("Distribute Skill Points")
            hp_p = st.number_input("Add Health (+10 per point)", 0, st.session_state.skill_points, 0, key="hp_p")
            mana_p = st.number_input("Add Mana (+10 per point)", 0, st.session_state.skill_points, 0, key="mana_p")
            str_p = st.number_input("Add Strength", 0, st.session_state.skill_points, 0, key="str_p")
            agi_p = st.number_input("Add Agility", 0, st.session_state.skill_points, 0, key="agi_p")
            if st.button("Apply skill points"):
                apply_skill_points(hp_p, mana_p, str_p, agi_p)
        else:
            if st.session_state.in_combat:
                st.subheader(f"Combat with {st.session_state.enemy['name']}")
                st.write(f"Enemy Health: {st.session_state.enemy_health}/{st.session_state.enemy['health']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⚔️ Basic Attack"):
                        player_attack()
                with col2:
                    if st.button("🔥 Cast Spell (20 MP)"):
                        cast_spell()
                with col3:
                    if st.button("🛡 Guard"):
                        st.session_state.message_log.append("You raise your guard!")
                        st.session_state.player_buffs["blocking"] = True
                        
                st.markdown("---")
                st.subheader("Class Skills")
                class_skills = CLASSES[st.session_state.player_class]["skills"]
                for skill, details in class_skills.items():
                    if st.button(f"{skill} ({details['cost']} MP)"):
                        if st.session_state.mana >= details["cost"]:
                            st.session_state.mana -= details["cost"]
                            player_attack(skill)
                        else:
                            st.session_state.message_log.append(f"Not enough mana for {skill}!")

            elif st.session_state.in_puzzle:
                st.subheader("Puzzle")
                puzzle = PUZZLES[st.session_state.floor]
                st.write(puzzle["question"])
                answer = st.text_input("Your answer:")
                if st.button("Submit Answer"):
                    solve_puzzle(answer)
            else:
                if st.session_state.floor <= MAX_FLOOR:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Explore"):
                            try_encounter()
                    with col2:
                        if st.button("Rest"):
                            rest()
                else:
                    st.success("Congratulations! You've conquered the tower!")
                    if st.button("Play Again"):
                        init_game()