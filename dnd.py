import streamlit as st
import random

st.set_page_config(page_title="Simple DnD with Stats", layout="centered")
st.title("🛡 Simple DnD Game - Stats in Combat")

CLASSES = {
    "Knight": {
        "image_url": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXpuMmcwOHBpaDNhaGd3MnZvNW0ya3k0dncxbmNtMmU2YTNld2FvdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bHSkKRvkRvy5chUBBp/200.webp",  
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
        "image_url": "https://media0.giphy.com/media/4N7vyQva5gsOKR3UKx/giphy.gif?cid=6c09b95218j83nhhxmj8gew7z29sydt5rauew5rrlp44tp9z&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g",  
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
        "image_url": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmJqamM3bjI3Y2MyZTE0dnBtM2I4aGg3eDR2dmVuM2Q4OGhicTZnNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/tx8UtrSC02lXO/200.webp", 
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
    1: [{"name": "Goblin", "health": 40, "strength": 10, "agility": 5, "image url":"https://media.tenor.com/ctiUtWQcDwEAAAAM/goblin-slayer-im-here.gif"}],
    2: [{"name": "Orc", "health": 60, "strength": 14, "agility": 7, "image url": "https://media.tenor.com/MyP7Y1C7pxoAAAAM/orc-dance-orc.gif"}],
    3: [{"name": "Troll", "health": 80, "strength": 18, "agility": 6, "image url": "https://media.giphy.com/media/t37AoeUoDpVeg/giphy.gif"}],
    4: [{"name": "Wraith", "health": 90, "strength": 20, "agility": 12,"image url":"https://i.redd.it/xqohgafrw3cc1.gif"}],
    5: [{"name": "Warlock", "health": 100, "strength": 22, "agility": 8, "image url":"https://media0.giphy.com/media/xUOwFToDIeaXgTblII/200w.gif?cid=6c09b952rj71te75dg0htluvvkxmdmqpev7uixglu2xb2oa1&ep=v1_gifs_search&rid=200w.gif&ct=g",}],
    6: [{"name": "Dread Knight", "health": 110, "strength": 25, "agility": 10,"image url":"data:image/jpeg;base64,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"}],
    7: [{"name": "Fire Elemental", "health": 130, "strength": 28, "agility": 10,"image url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT3ajkIS1qUIp696u6DpartAo4MKAz8QlnTfQ&s"}],
    8: [{"name": "Ice Golem", "health": 150, "strength": 32, "agility": 8,"image url":"https://i.pinimg.com/originals/c3/69/ce/c369ce2d03e8034929ad42c2fe76b7d0.gif"}],
    9: [{"name": "Necromancer", "health": 120, "strength": 35, "agility": 15,"image url":"https://media.tenor.com/FO5gvaU-oLsAAAAM/kastor-necromancer-diablo4-necromancer-diablo.gif"}],
    10: [{"name": "Hellhound", "health": 160, "strength": 38, "agility": 18,"image url":"https://i.pinimg.com/originals/dd/36/6e/dd366ea2a91e5725faa553f3dfb77ed7.gif"}],
}

BOSSES = {
    1: {"name": "Goblin King", "health": 100, "strength": 20, "agility": 10, "description": "The brutal Goblin King.","image url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReDtzIdHNyQJ-4ILxM-oO7ZStRdl41P1rIwi8cbi_XGt3cvb62ArwQk_L2AB9TowH_ctc&usqp=CAU"},
    2: {"name": "Orc Warlord", "health": 240, "strength": 28, "agility": 12, "description": "The fearsome Orc commander.","image url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ3K3POAdR-7gt8TNwNjQjvMU2bVEEPD4vnfw&s"},
    3: {"name": "Dark Dragon", "health": 280, "strength": 35, "agility": 15, "description": "A mighty dragon shrouded in darkness.","image url":"https://i.pinimg.com/originals/bc/4c/d9/bc4cd952773dcacca22ef7ada5c7163d.gif"},
    4: {"name": "Shadow Lurker", "health": 260, "strength": 30, "agility": 20, "description": "A deadly phantom of the shadows.","image url":"https://i.pinimg.com/originals/74/a5/3e/74a53ef35a0f47ded85bed8eba20c9d0.gif"},
    5: {"name": "Ancient Warlock", "health": 290, "strength": 42, "agility": 24, "description": "Master of forbidden magic.","image url":"data:image/jpeg;base64,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"},
    6: {"name": "Doom Bringer", "health": 220, "strength": 40, "agility": 18, "description": "Harbinger of the world's end.","image url":"https://i.pinimg.com/originals/c9/ea/b6/c9eab670fda694b8673101fbe6227866.gif"},
    7: {"name": "Phoenix King", "health": 240, "strength": 45, "agility": 22, "description": "Ruler of the fiery realms.","image url":"https://i.pinimg.com/originals/8b/4f/1f/8b4f1f8f63271e454bcf8f1d59d8fa0e.gif"},
    8: {"name": "Frost Titan", "health": 260, "strength": 50, "agility": 18, "description": "Towering giant of eternal ice.","image url":"https://static.wikia.nocookie.net/powerlisting/images/7/71/HyorinmaruToshiro.gif/revision/latest/thumbnail/width/360/height/360?cb=20181116124049"},
    9: {"name": "Lich King", "health": 280, "strength": 55, "agility": 25, "description": "Undead monarch of the damned.","image url":"https://media.tenor.com/xyCBgyc2dqEAAAAM/wow.gif"},
    10: {"name": "Demon Lord", "health": 50000, "strength": 70, "agility": 60, "description": "The supreme ruler of the abyss.","image url":"https://i.pinimg.com/originals/3a/db/43/3adb4385b0ad8e89bd73c287433d3359.gif"},
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
        player_image=stats["image_url"],  
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
     if st.session_state.in_combat:
                st.subheader(f"Combat with {st.session_state.enemy['name']}")
                
                if "image url" in st.session_state.enemy:
                    st.image(st.session_state.enemy["image url"], width=200)
                
                st.write(f"Enemy Health: {st.session_state.enemy_health}/{st.session_state.enemy['health']}")
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


if "player_class" not in st.session_state:
    init_game()

if "player_class" not in st.session_state:
    init_game()

if not st.session_state.player_class:
    st.header("Choose Your Starter Class")
    cols = st.columns(3)
    for i, (c, info) in enumerate(CLASSES.items()):
        with cols[i]:
            st.subheader(c)
            st.image(info["image_url"], width=200)  
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
                
                if "image url" in st.session_state.enemy:
                    st.image(st.session_state.enemy["image url"], width=200)
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
                st.subheader("Puzzle Encounter")
                
                st.image("https://media.tenor.com/Y2jZZeojXg8AAAAM/puzzle-angry.gif", 
                        width=200)
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