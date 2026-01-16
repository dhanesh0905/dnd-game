"""
A Streamlit-based dnd game where players choose a character class, battle enemies, 
solve puzzles, and progress through floors of a tower. Includes character progression 
through skill points and combat mechanics.

Imports:
    json: For loading game data and serialization
    streamlit (st): For creating the web UI
    random: For game randomization
    general: Custom game utility functions
    encounter: Custom encounter handling functions
    datetime: for saving game state with timestamps
    os: For file operations
    pickle: For object serialization
"""
import json
import streamlit as st
import random
import general
import encounter
import datetime
import os
import pickle


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


class GameState:
    """Class to encapsulate game state for persistence"""
    def __init__(self):
        self.player_class = None
        self.player_image = None
        self.health = 0
        self.max_health = 0
        self.mana = 0
        self.max_mana = 0
        self.strength = 0
        self.agility = 0
        self.floor = 1
        self.skill_points = 0
        self.pending_skill_points = False
        self.in_combat = False
        self.enemy = None
        self.enemy_health = 0
        self.in_puzzle = False
        self.puzzle_solved = False
        self.message_log = []
        self.game_over = False
        self.fighting_boss = False
        self.solved_puzzles = set()
        self.enemies_defeated = 0
        self.defeated_enemies = set()
        self.encountered_by_floor = {}
        self.save_timestamp = None
    
    def to_dict(self):
        """Convert game state to dictionary for JSON serialization"""
        return {
            'player_class': self.player_class,
            'player_image': self.player_image,
            'health': self.health,
            'max_health': self.max_health,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'strength': self.strength,
            'agility': self.agility,
            'floor': self.floor,
            'skill_points': self.skill_points,
            'pending_skill_points': self.pending_skill_points,
            'in_combat': self.in_combat,
            'enemy': self.enemy,
            'enemy_health': self.enemy_health,
            'in_puzzle': self.in_puzzle,
            'puzzle_solved': self.puzzle_solved,
            'message_log': self.message_log,
            'game_over': self.game_over,
            'fighting_boss': self.fighting_boss,
            'solved_puzzles': list(self.solved_puzzles),
            'enemies_defeated': self.enemies_defeated,
            'defeated_enemies': list(self.defeated_enemies),
            'encountered_by_floor': self.encountered_by_floor,
            'save_timestamp': datetime.datetime.now().isoformat()
        }
    
    def from_dict(self, data):
        """Load game state from dictionary"""
        self.player_class = data['player_class']
        self.player_image = data['player_image']
        self.health = data['health']
        self.max_health = data['max_health']
        self.mana = data['mana']
        self.max_mana = data['max_mana']
        self.strength = data['strength']
        self.agility = data['agility']
        self.floor = data['floor']
        self.skill_points = data['skill_points']
        self.pending_skill_points = data['pending_skill_points']
        self.in_combat = data['in_combat']
        self.enemy = data['enemy']
        self.enemy_health = data['enemy_health']
        self.in_puzzle = data['in_puzzle']
        self.puzzle_solved = data['puzzle_solved']
        self.message_log = data['message_log']
        self.game_over = data['game_over']
        self.fighting_boss = data['fighting_boss']
        self.solved_puzzles = set(data['solved_puzzles'])
        self.enemies_defeated = data['enemies_defeated']
        self.defeated_enemies = set(data['defeated_enemies'])
        self.encountered_by_floor = data['encountered_by_floor']
        self.save_timestamp = data.get('save_timestamp')


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
    msg = f"You use {skill} and deal {damage} damage!" if skill else f"You dealt {damage} damage"
    if crit:
        msg += " (Critical hit!)"
    st.session_state.message_log.append(msg)

    if st.session_state.enemy_health <= 0:
        general.handle_victory(st.session_state, encounter, BOSSES, BASE_SKILL_POINTS)
        save_game_state()
    else:
        enemy_attack()


def start_game(chosen_class):
    """
    Initialize game state for new game

    Args:
        chosen_class (str): Player's selected character class
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
    
    Uses two formats: JSON for human readability and pickle for complete object serialization
    """
    try:
        # Create GameState object for serialization
        game_state = GameState()
        game_state.from_dict(st.session_state.to_dict())
        
        # Save as JSON (human readable)
        save_data = game_state.to_dict()
        json_filename = f"dnd_save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(json_filename, 'w') as f:
            json.dump(save_data, f, indent=4)
            
        # Save as pickle (complete object)
        pickle_filename = f"dnd_save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        with open(pickle_filename, 'wb') as f:
            pickle.dump(game_state, f)
            
        st.session_state.message_log.append(f"Game saved to {json_filename} and {pickle_filename}")
        
        # Update timestamp in session state
        st.session_state.save_timestamp = save_data['save_timestamp']
        
    except Exception as e:
        st.session_state.message_log.append(f"Error saving game: {str(e)}")


def load_game_state(filename):
    """
    Load game state from file
    
    Args:
        filename (str): Path to save file
    """
    try:
        if filename.endswith('.json'):
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            # Create GameState object and load data
            game_state = GameState()
            game_state.from_dict(save_data)
            
        elif filename.endswith('.pkl'):
            with open(filename, 'rb') as f:
                game_state = pickle.load(f)
        else:
            st.session_state.message_log.append("Unsupported file format")
            return False
        
        # Update session state from loaded game state
        st.session_state.player_class = game_state.player_class
        st.session_state.player_image = game_state.player_image
        st.session_state.health = game_state.health
        st.session_state.max_health = game_state.max_health
        st.session_state.mana = game_state.mana
        st.session_state.max_mana = game_state.max_mana
        st.session_state.strength = game_state.strength
        st.session_state.agility = game_state.agility
        st.session_state.floor = game_state.floor
        st.session_state.skill_points = game_state.skill_points
        st.session_state.pending_skill_points = game_state.pending_skill_points
        st.session_state.in_combat = game_state.in_combat
        st.session_state.enemy = game_state.enemy
        st.session_state.enemy_health = game_state.enemy_health
        st.session_state.in_puzzle = game_state.in_puzzle
        st.session_state.puzzle_solved = game_state.puzzle_solved
        st.session_state.message_log = game_state.message_log
        st.session_state.game_over = game_state.game_over
        st.session_state.fighting_boss = game_state.fighting_boss
        st.session_state.solved_puzzles = game_state.solved_puzzles
        st.session_state.enemies_defeated = game_state.enemies_defeated
        st.session_state.defeated_enemies = game_state.defeated_enemies
        st.session_state.encountered_by_floor = game_state.encountered_by_floor
        st.session_state.save_timestamp = game_state.save_timestamp
        
        st.session_state.message_log.append(f"Game loaded from {filename}")
        return True
        
    except Exception as e:
        st.session_state.message_log.append(f"Error loading game: {str(e)}")
        return False


def list_save_files():
    """List all available save files"""
    json_files = [f for f in os.listdir('.') if f.startswith('dnd_save_') and f.endswith('.json')]
    pickle_files = [f for f in os.listdir('.') if f.startswith('dnd_save_') and f.endswith('.pkl')]
    return sorted(json_files + pickle_files, reverse=True)


def delete_save_file(filename):
    """Delete a save file"""
    try:
        os.remove(filename)
        st.session_state.message_log.append(f"Deleted save file: {filename}")
        return True
    except Exception as e:
        st.session_state.message_log.append(f"Error deleting file: {str(e)}")
        return False


def enemy_attack():
    """
    Execute enemy attack in combat
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
        save_game_state()


def solve_puzzle(answer):
    """
    Validate puzzle solution and handle results

    Args:
        answer (str): Player's solution to the puzzle
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
        save_game_state()
        try_encounter()
    else:
        st.session_state.message_log.append("Wrong answer, try again.")
        st.session_state.in_combat = False


def next_floor():
    """
    Advance player to next floor of the tower
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
        save_game_state()
    else:
        st.session_state.message_log.append("You have reached the top of the tower!")
        st.session_state.game_over = True
        save_game_state()


def try_encounter():
    """
    Attempt to trigger random encounter
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
            general.handle_victory(st.session_state, encounter, BOSSES, BASE_SKILL_POINTS)
            save_game_state()
        else:
            enemy_attack()
    else:
        st.session_state.message_log.append("Not enough mana to cast a spell!")


def rest():
    """
    Rest to recover health and mana
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
    
    # Load saved games section
    save_files = list_save_files()
    if save_files:
        with st.expander("📂 Load Saved Game", expanded=False):
            st.write("Available save files (newest first):")
            for save_file in save_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(save_file)
                with col2:
                    if st.button("Load", key=f"load_{save_file}"):
                        if load_game_state(save_file):
                            st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_{save_file}"):
                        if delete_save_file(save_file):
                            st.rerun()
    
    st.markdown("---")
    st.subheader("New Game")
    
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
                st.rerun()
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
    
    # Save/Load section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Save/Load")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Save Game"):
            save_game_state()
            st.rerun()
    with col2:
        if st.button("Quick Load"):
            save_files = list_save_files()
            if save_files:
                load_game_state(save_files[0])
                st.rerun()
            else:
                st.sidebar.warning("No save files found")
    
    # Show last save time if available
    if hasattr(st.session_state, 'save_timestamp') and st.session_state.save_timestamp:
        try:
            save_time = datetime.datetime.fromisoformat(st.session_state.save_timestamp)
            st.sidebar.caption(f"Last save: {save_time.strftime('%H:%M:%S')}")
        except:
            pass

    # Game over screen
    if st.session_state.game_over:
        st.error("💀 You died! Game Over." if st.session_state.health <= 0 else "🎉 You conquered all floors! You win!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Restart"):
                general.init_game(st.session_state, FLOOR_STORY[0])
                st.rerun()
        with col2:
            if st.button("Save Final State"):
                save_game_state()
                st.rerun()
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
                    st.rerun()
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
                        st.rerun()
                    if st.button("🔥 Cast Spell (20 MP)"):
                        cast_spell()
                        st.rerun()
                with col2:
                    if st.button("🛡 Guard"):
                        st.session_state.message_log.append("You raise your guard!")
                        enemy_attack()
                        st.rerun()

                st.markdown("---")
                st.subheader("Class Skills")
                class_skills = CLASSES[st.session_state.player_class]["skills"]
                for skill, details in class_skills.items():
                    if st.button(f"{skill} ({details['cost']} MP)"):
                        player_attack(skill)
                        st.rerun()
            
            # Puzzle interface
            elif st.session_state.in_puzzle:
                st.subheader("Puzzle Encounter")
                st.image("https://media.tenor.com/Y2jZZeojXg8AAAAM/puzzle-angry.gif", width=200)
                puzzle = PUZZLES[st.session_state.floor]
                st.write(puzzle["question"])
                answer = st.text_input("Your answer:")
                if st.button("Submit Answer"):
                    solve_puzzle(answer)
                    st.rerun()

            # Exploration interface
            else:
                if st.session_state.floor <= MAX_FLOOR:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔍 Explore"):
                            try_encounter()
                            st.rerun()
                    with col2:
                        if st.button("💤 Rest"):
                            rest()
                            st.rerun()
                    with col3:
                        if st.button("💾 Quick Save"):
                            save_game_state()
                            st.rerun()
                else:
                    st.success("Congratulations! You've conquered the tower!")
                    if st.button("Play Again"):
                        general.init_game(st.session_state, FLOOR_STORY[0])