"""
A Streamlit-based dnd game where players choose a character class, battle enemies, 
solve puzzles, and progress through floors of a tower. Includes character progression 
through skill points and combat mechanics.

Imports:
    json: For loading game data
    streamlit (st): For creating the web UI
    random: For game randomization
    general: Custom game utility functions
    encounter: Custom encounter handling functions
    datatime: for saving game state with timestamps
"""
import json
import streamlit as st
import random
import general
import encounter
import datetime  # Added for timestamp in save files
# Load game data from JSON file
with open('dnd_game_data.json', 'r') as f:
    game_data = json.load(f)


CLASSES = game_data['CLASSES']
ENEMIES = {int(k): v for k, v in game_data['ENEMIES'].items()}
BOSSES = {int(k): v for k, v in game_data['BOSSES'].items()}
PUZZLES = {int(k): v for k, v in game_data['PUZZLES'].items()}
FLOOR_STORY = {int(k): v for k, v in game_data['FLOOR_STORY'].items()}

MAX_FLOOR = 10
BASE_SKILL_POINTS = 5


def apply_skill_points(hp_points, mana_points, str_points, agi_points):
    """
    Distribute skill points to character attributes

    Args:
        hp_points (int): Points to allocate to health
        mana_points (int): Points to allocate to mana
        str_points (int): Points to allocate to strength
        agi_points (int): Points to allocate to agility

    Returns:
        bool: True if points were successfully applied, False otherwise

    Side Effects:
        - Updates character attributes in session state
        - Reduces available skill points
        - Displays error message if invalid distribution
        - Saves game state to JSON after successful application
    """
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
    
    # Save game after applying points
    save_game_state()
    return True


def player_attack(skill=None):
    """
    Execute player's attack 

    Args:
        skill (str, optional): Specific skill to use. Defaults to basic attack.

    Side Effects:
        - Calculates damage based on stats and skill
        - Updates enemy health
        - Triggers enemy counterattack or victory
        - Updates combat log
        - Manages mana consumption
    """
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
    msg = f"You use {skill} and deal {damage} damage!" if skill else f"You delt {damage} damage"
    if crit:
        msg += " (Critical hit!)"
    st.session_state.message_log.append(msg)

    if st.session_state.enemy_health <= 0:
        general.handle_victory(st.session_state, encounter, BOSSES,  BASE_SKILL_POINTS)
    else:
        enemy_attack()


def start_game(chosen_class):
    """
    Initialize game state for new game

    Args:
        chosen_class (str): Player's selected character class

    Side Effects:
        - Resets session state with initial values
        - Sets character stats based on class
        - Initializes game progression tracking
        - Creates initial JSON save file
    """
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
        message_log=[FLOOR_STORY[1],
                     f"You chose {chosen_class}. {stats['description']} Enjoy!"],
        game_over=False,
        skill_points=0,
        pending_skill_points=False,
        fighting_boss=False,
        solved_puzzles=set(),
        enemies_defeated=0,
        defeated_enemies=set(),
        encountered_by_floor={},
    )
    # Create initial save file
    save_game_state()
    
    
def save_game_state():
    """
    Save current game state to a JSON file
    
    Side Effects:
        - Creates/overwrites dnd_gama_data.json with current state
        - Saves character stats, inventory, and progress in JSON format
    """
    try:
        save_data = {
            "player_class": st.session_state.player_class,
            "player_image": st.session_state.player_image,
            "health": st.session_state.health,
            "max_health": st.session_state.max_health,
            "mana": st.session_state.mana,
            "max_mana": st.session_state.max_mana,
            "strength": st.session_state.strength,
            "agility": st.session_state.agility,
            "floor": st.session_state.floor,
            "in_combat": st.session_state.in_combat,
            "enemy": st.session_state.enemy,
            "enemy_health": st.session_state.enemy_health,
            "in_puzzle": st.session_state.in_puzzle,
            "puzzle_solved": st.session_state.puzzle_solved,
            "message_log": st.session_state.message_log,
            "game_over": st.session_state.game_over,
            "skill_points": st.session_state.skill_points,
            "pending_skill_points": st.session_state.pending_skill_points,
            "fighting_boss": st.session_state.fighting_boss,
            "solved_puzzles": list(st.session_state.solved_puzzles),  # Convert set to list
            "enemies_defeated": st.session_state.enemies_defeated,
            "defeated_enemies": list(st.session_state.defeated_enemies),  # Convert set to list
            "encountered_by_floor": st.session_state.encountered_by_floor,
            "last_save": str(datetime.datetime.now())
        }
        
        with open('dnd_gama_data.json', 'w') as f:
            json.dump(save_data, f, indent=4)
            
        st.session_state.message_log.append("Game progress saved to JSON successfully!")
    except Exception as e:
        st.session_state.message_log.append(f"Error saving game: {str(e)}")
 
 
def save_combat_log():
    """
    Save combat log to the JSON file
    
    Side Effects:
        - Updates dnd_gama_data.json with combat history
        - Preserves all game data while adding combat log
    """
    try:
        # First load existing data to preserve all game state
        try:
            with open('dnd_gama_data.json', 'r') as f:
                save_data = json.load(f)
        except FileNotFoundError:
            save_data = {}
        
        # Filter combat-related messages
        combat_messages = []
        for msg in st.session_state.message_log:
            if "damage" in msg or "hit" in msg or "cast" in msg or "evade" in msg or "attack" in msg:
                combat_messages.append(msg)
        
        # Add combat log to save data
        save_data["combat_log"] = combat_messages
        save_data["combat_log_saved_at"] = str(datetime.datetime.now())
        
        with open('dnd_gama_data.json', 'w') as f:
            json.dump(save_data, f, indent=4)
            
        st.session_state.message_log.append("Combat log saved to JSON!")
    except Exception as e:
        st.session_state.message_log.append(f"Error saving combat log: {str(e)}")
        

def enemy_attack():
    """
    Execute enemy attack in combat

    Side Effects:
        - Calculates damage based on enemy stats
        - Applies damage to player
        - Checks for player death
        - Updates combat log
        - Handles evasion mechanics
    """
    if not st.session_state.in_combat or st.session_state.game_over or not st.session_state.enemy:
        return

    enemy = BOSSES[st.session_state.floor] if st.session_state.fighting_boss else st.session_state.enemy
    enemy_power = enemy["strength"]
    enemy_agility = enemy.get("agility", 5) 
    evasion_chance = max(0.05, (st.session_state.agility - enemy_agility) /100)
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
    """
    Validate puzzle solution and handle results

    Args:
        answer (str): Player's solution to the puzzle

    Side Effects:
        - Checks answer against correct solution
        - Awards skill points for correct answers
        - Triggers encounters after puzzle
        - Updates puzzle tracking state
    """
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
        st.session_state.in_combat = False


def next_floor():
    """
    Advance player to next floor of the tower

    Side Effects:
        - Increments floor counter
        - Resets floor-specific states
        - Displays story for new floor
        - Handles game completion
    """
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
    """
    Attempt to trigger random encounter

    Side Effects:
        - Starts puzzle or combat encounter
        - Handles encounter probability
        - Skips encounters when inappropriate
    """
    if st.session_state.in_combat or st.session_state.game_over or st.session_state.in_puzzle:
        return

    if (st.session_state.floor not in st.session_state.solved_puzzles and 
        random.random() < 0.3 and 
        st.session_state.floor in PUZZLES):
        encounter.start_puzzle(st.session_state, PUZZLES)
    else:
        encounter.encounter_enemy(st.session_state, next_floor, MAX_FLOOR, ENEMIES, random)


def cast_spell():
    """
    Cast spells in combat

    Side Effects:
        - Deals spell damage to enemy
        - Consumes mana
        - Triggers enemy counterattack
        - Updates combat log
    """
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
    """
    Rest to recover health and mana

    Side Effects:
        - Restores HP and mana
        - Triggers random encounter
        - Updates game log
        - Saves game state to JSON after resting
    """
    if st.session_state.in_combat or st.session_state.game_over or st.session_state.in_puzzle:
        return

    heal_amount = min(30, st.session_state.max_health - st.session_state.health)
    mana_amount = min(30, st.session_state.max_mana - st.session_state.mana)
    st.session_state.health += heal_amount
    st.session_state.mana += mana_amount
    st.session_state.message_log.append(f"You rest and recover {heal_amount} HP and {mana_amount} mana.")
    
    # Save game after resting
    save_game_state()
    try_encounter()


# Initialize game state
if "player_class" not in st.session_state:
    general.init_game(st.session_state, FLOOR_STORY[0])


# Class selection screen
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
                chosen_class = st.session_state.player_class
                start_game(c)
else:
    # Main game interface
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

    # Game over screen
    if st.session_state.game_over:
        st.error("💀 You died! Game Over." if st.session_state.health <= 0 else "🎉 You conquered all floors! You win!")
        if st.button("Restart"):
                general.init_game(st.session_state, FLOOR_STORY[0]) 
    else:
        # Game log display
        st.subheader("Game Log")
        log_container = st.container(height=300)
        with log_container:
            for msg in reversed(st.session_state.message_log[-10:]):
                if msg.startswith("![Boss]("):
                    st.image(msg.split("(")[1].split(")")[0], width=200)
                else:
                    st.write(msg)

        # Skill point distribution
        if st.session_state.pending_skill_points and st.session_state.skill_points > 0:
            with st.expander("Distribute Skill Points", expanded=True):
                hp_p = st.number_input("Add Health (+10 per point)", 0, st.session_state.skill_points, 0, key="hp_p")
                mana_p = st.number_input("Add Mana (+10 per point)", 0, st.session_state.skill_points, 0, key="mana_p")
                str_p = st.number_input("Add Strength", 0, st.session_state.skill_points, 0, key="str_p")
                agi_p = st.number_input("Add Agility", 0, st.session_state.skill_points, 0, key="agi_p")
                if st.button("Apply skill points"):
                    apply_skill_points(hp_p, mana_p, str_p, agi_p)
        else:
            # Combat interface
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
            
            # Puzzle interface
            elif st.session_state.in_puzzle:
                st.subheader("Puzzle Encounter")
                st.image("https://media.tenor.com/Y2jZZeojXg8AAAAM/puzzle-angry.gif", width=200)
                puzzle = PUZZLES[st.session_state.floor]
                st.write(puzzle["question"])
                answer = st.text_input("Your answer:")
                if st.button("Submit Answer"):
                    solve_puzzle(answer)

            # Exploration interface
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
                        #finished the game yay!!!