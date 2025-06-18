from collections import deque
import json
import streamlit as st
import random
import general
import encounter 

with open('data.json', 'r') as f:
    game_data = json.load(f)

CLASSES = game_data['CLASSES']
ENEMIES = {int(k): v for k, v in game_data['ENEMIES'].items()}
BOSSES = {int(k): v for k, v in game_data['BOSSES'].items()}
PUZZLES = {int(k): v for k, v in game_data['PUZZLES'].items()}
FLOOR_STORY = {int(k): v for k, v in game_data['FLOOR_STORY'].items()}

MAX_FLOOR = 10
BASE_SKILL_POINTS = 5

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

def player_attack(skill=None):
    if not st.session_state.in_combat or st.session_state.game_over:
        return

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
    damage = max(1, base_damage + (base_damage // 2 if crit else 0) - random.randint(0, 3))
    
    st.session_state.enemy_health -= damage
    msg = f"You use {skill} and deal {damage} damage!" if skill else f"You attack dealing {damage} damage"
    if crit:
        msg += " (Critical hit!)"
    st.session_state.message_log.append(msg)

    if st.session_state.enemy_health <= 0:
        general.handle_victory(st.session_state, encounter, BOSSES,  BASE_SKILL_POINTS)
    else:
        enemy_attack()


def start_game(chosen_class):
    stats = CLASSES[chosen_class]
    st.session_state.update(
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
        enemies_defeated=0,
        defeated_enemies=set(),
        encountered_by_floor={},
    )
    
def enemy_attack():
    if not st.session_state.in_combat or st.session_state.game_over or not st.session_state.enemy:
        return

    enemy = BOSSES[st.session_state.floor] if st.session_state.fighting_boss else st.session_state.enemy
    enemy_power = enemy["strength"]
    enemy_agility = enemy.get("agility", 5)
    
    evasion_chance = max(0.05, (st.session_state.agility - enemy_agility) / 100)
    if random.random() < evasion_chance:
        st.session_state.message_log.append("You evaded the enemy's attack!")
        return
    
    damage = max(1, enemy_power - (st.session_state.agility // 3))
    st.session_state.health -= damage
    st.session_state.message_log.append(f"Enemy hits you for {damage} damage.")
    
    if st.session_state.health <= 0:
        st.session_state.health = 0
        st.session_state.game_over = True
        st.session_state.message_log.append("You died. Game over.")

def solve_puzzle(answer):
    if not st.session_state.in_puzzle or st.session_state.floor not in PUZZLES:
        return

    correct = PUZZLES[st.session_state.floor]["answer"]
    if answer.strip().lower() == correct:
        st.session_state.solved_puzzles.add(st.session_state.floor)
        st.session_state.puzzle_solved = True
        st.session_state.in_puzzle = False
        st.session_state.message_log.append("Puzzle solved! You may proceed.")
        st.session_state.skill_points += BASE_SKILL_POINTS
        st.session_state.pending_skill_points = True
        try_encounter()
    else:
        st.session_state.message_log.append("Wrong answer, try again.")


def next_floor():
    if st.session_state.floor < MAX_FLOOR:
        st.session_state.floor += 1
        st.session_state.enemies_defeated = 0
        st.session_state.message_log.append(f"You advance to floor {st.session_state.floor}.")
        st.session_state.message_log.append(FLOOR_STORY[st.session_state.floor])
        st.session_state.in_combat = False
        st.session_state.enemy = None
        st.session_state.enemy_health = 0
        st.session_state.in_puzzle = False
        st.session_state.puzzle_solved = False
        st.session_state.fighting_boss = False
    else:
        st.session_state.message_log.append("You have reached the top of the tower!")
        st.session_state.game_over = True

def try_encounter():
    if st.session_state.in_combat or st.session_state.game_over or st.session_state.in_puzzle:
        return

    if (st.session_state.floor not in st.session_state.solved_puzzles and 
        random.random() < 0.3 and 
        st.session_state.floor in PUZZLES):
        encounter.start_puzzle(st.session_state, PUZZLES)
    else:
        encounter.encounter_enemy(st.session_state ,next_floor, MAX_FLOOR, ENEMIES , random )

def cast_spell():
    if not st.session_state.in_combat or st.session_state.game_over:
        return

    if st.session_state.mana >= 20:
        st.session_state.mana -= 20
        base_damage = st.session_state.strength + 10
        damage = max(1, base_damage - random.randint(0, 5))
        st.session_state.enemy_health -= damage
        st.session_state.message_log.append(f"You cast a spell dealing {damage} damage!")
        
        if st.session_state.enemy_health <= 0:
            general.handle_victory(st.session_state, encounter, BOSSES,  BASE_SKILL_POINTS)
        else:
            enemy_attack()
    else:
        st.session_state.message_log.append("Not enough mana to cast a spell!")

def rest():
    if st.session_state.in_combat or st.session_state.game_over or st.session_state.in_puzzle:
        return

    heal_amount = min(30, st.session_state.max_health - st.session_state.health)
    mana_amount = min(30, st.session_state.max_mana - st.session_state.mana)
    st.session_state.health += heal_amount
    st.session_state.mana += mana_amount
    st.session_state.message_log.append(f"You rest and recover {heal_amount} HP and {mana_amount} mana.")
    try_encounter()

if "player_class" not in st.session_state:
    general.init_game(st.session_state, FLOOR_STORY[0])


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
                chosen_class= st.session_state.player_class
                start_game(c)
else:
    
    st.sidebar.header(f"Status - Floor {st.session_state.floor}")
    st.sidebar.image(st.session_state.player_image, width=200)
    st.sidebar.write(f"Class: {st.session_state.player_class}")
    st.sidebar.progress(st.session_state.health / st.session_state.max_health, 
                       text=f"❤ Health: {st.session_state.health}/{st.session_state.max_health}")
    st.sidebar.progress(st.session_state.mana / st.session_state.max_mana, 
                       text=f"🔵 Mana: {st.session_state.mana}/{st.session_state.max_mana}")
    st.sidebar.write(f"💪 Strength: {st.session_state.strength}")
    st.sidebar.write(f"🤸 Agility: {st.session_state.agility}")
    st.sidebar.write(f"⭐ Skill Points: {st.session_state.skill_points}")

    if st.session_state.game_over:
        st.error("💀 You died! Game Over." if st.session_state.health <= 0 else "🎉 You conquered all floors! You win!")
        if st.button("Restart"):
                general.init_game(st.session_state, FLOOR_STORY[0]) 
    else:
        
        st.subheader("Game Log")
        log_container = st.container(height=300)
        with log_container:
            for msg in reversed(st.session_state.message_log[-10:]):
                
                if msg.startswith("![Boss]("):
                    st.image(msg.split("(")[1].split(")")[0], width=200)
                else:
                    st.write(msg)

        
        if st.session_state.pending_skill_points and st.session_state.skill_points > 0:
            with st.expander("Distribute Skill Points", expanded=True):
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
                
                st.progress(st.session_state.enemy_health / st.session_state.enemy['health'], 
                          text=f"Enemy Health: {st.session_state.enemy_health}/{st.session_state.enemy['health']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⚔️ Basic Attack"):
                        player_attack()
                    if st.button("🔥 Cast Spell (20 MP)"):
                        cast_spell()
                with col2:
                    if st.button("🛡 Guard"):
                        st.session_state.message_log.append("You raise your guard!")
                        enemy_attack()
                
                st.markdown("---")
                st.subheader("Class Skills")
                class_skills = CLASSES[st.session_state.player_class]["skills"]
                for skill, details in class_skills.items():
                    if st.button(f"{skill} ({details['cost']} MP)"):
                        player_attack(skill)

            elif st.session_state.in_puzzle:
                st.subheader("Puzzle Encounter")
                st.image("https://media.tenor.com/Y2jZZeojXg8AAAAM/puzzle-angry.gif", width=200)
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
                        general.init_game(st.session_state, FLOOR_STORY[0])