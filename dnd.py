"""
A Streamlit-based D&D game with OOP structure and serialization.
"""

import json
import streamlit as st
import random
import general
import encounter
import datetime
import os
import pickle


class GameState:
    def __init__(self):
        self.reset()
    
    def reset(self):
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
        
        # Combat state
        self.in_combat = False
        self.enemy = None
        self.enemy_health = 0
        self.fighting_boss = False
        
        # Puzzle state
        self.in_puzzle = False
        self.puzzle_solved = False
        
        # Progress tracking
        self.defeated_enemies = set()
        self.solved_puzzles = set()
        self.message_log = []
        self.game_over = False
        self.enemies_defeated = 0
        self.save_timestamp = None
    
    def to_dict(self):
        """Convert game state to dictionary for serialization"""
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
            'fighting_boss': self.fighting_boss,
            'in_puzzle': self.in_puzzle,
            'puzzle_solved': self.puzzle_solved,
            'defeated_enemies': list(self.defeated_enemies),
            'solved_puzzles': list(self.solved_puzzles),
            'message_log': self.message_log,
            'game_over': self.game_over,
            'enemies_defeated': self.enemies_defeated,
            'save_timestamp': datetime.datetime.now().isoformat() if not self.save_timestamp else self.save_timestamp
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
        self.fighting_boss = data['fighting_boss']
        self.in_puzzle = data['in_puzzle']
        self.puzzle_solved = data['puzzle_solved']
        self.defeated_enemies = set(data['defeated_enemies'])
        self.solved_puzzles = set(data['solved_puzzles'])
        self.message_log = data['message_log']
        self.game_over = data['game_over']
        self.enemies_defeated = data['enemies_defeated']
        self.save_timestamp = data.get('save_timestamp')


def save_game_to_json():
    """Save current game state to JSON file"""
    game = st.session_state.game
    save_data = game.to_dict()
    
    # Add metadata
    save_data['metadata'] = {
        'version': '1.0',
        'save_date': datetime.datetime.now().isoformat(),
        'game_name': 'D&D Tower Adventure'
    }
    
    filename = f"dnd_save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    game.message_log.append(f"Game saved to {filename}")
    return filename


def save_game_to_pickle():
    """Save current game state using pickle"""
    game = st.session_state.game
    filename = f"dnd_save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    
    with open(filename, 'wb') as f:
        pickle.dump(game, f)
    
    game.message_log.append(f"Game saved to {filename} (pickle format)")
    return filename


def load_game_from_json(filename):
    """Load game state from JSON file"""
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)
        
        game = GameState()
        game.from_dict(save_data)
        st.session_state.game = game
        game.message_log.append(f"Game loaded from {filename}")
        return True
    except Exception as e:
        st.error(f"Error loading game: {e}")
        return False


def load_game_from_pickle(filename):
    """Load game state from pickle file"""
    try:
        with open(filename, 'rb') as f:
            game = pickle.load(f)
        
        st.session_state.game = game
        game.message_log.append(f"Game loaded from {filename} (pickle format)")
        return True
    except Exception as e:
        st.error(f"Error loading game: {e}")
        return False


def list_save_files():
    """List all available save files"""
    json_files = [f for f in os.listdir('.') if f.startswith('dnd_save_') and f.endswith('.json')]
    pickle_files = [f for f in os.listdir('.') if f.startswith('dnd_save_') and f.endswith('.pkl')]
    return sorted(json_files + pickle_files, reverse=True)


def apply_skill_points(hp_points, mana_points, str_points, agi_points):
    """Distribute skill points to character attributes"""
    game = st.session_state.game
    
    total = hp_points + mana_points + str_points + agi_points
    if total > game.skill_points:
        st.error(f"Only {game.skill_points} skill points available.")
        return False
    
    game.max_health += hp_points * 10
    game.max_mana += mana_points * 10
    game.strength += str_points
    game.agility += agi_points
    
    # Restore to max
    game.health = game.max_health
    game.mana = game.max_mana
    game.skill_points -= total
    game.pending_skill_points = game.skill_points > 0
    
    return True


def player_attack(skill=None):
    """Execute player's attack in combat"""
    game = st.session_state.game
    classes = st.session_state.classes
    
    if not game.in_combat or game.game_over:
        return
    
    if skill:
        skill_info = classes[game.player_class]["skills"][skill]
        base_damage = int(game.strength * skill_info["damage_mult"])
        mana_cost = skill_info["cost"]
        
        if game.mana < mana_cost:
            game.message_log.append(f"Not enough mana for {skill}!")
            return
        
        game.mana -= mana_cost
        attack_type = skill
    else:
        base_damage = game.strength
        attack_type = "basic attack"
    
    # Calculate damage with crit chance
    crit_chance = min(0.3, game.agility / 100)
    crit = random.random() < crit_chance
    
    damage = max(1, base_damage + (base_damage // 2 if crit else 0) - random.randint(0, 3))
    game.enemy_health -= damage
    
    msg = f"You use {attack_type} and deal {damage} damage!"
    if crit:
        msg += " (Critical hit!)"
    game.message_log.append(msg)
    
    if game.enemy_health <= 0:
        general.handle_victory(game, encounter, st.session_state.bosses, st.session_state.base_skill_points)
    else:
        enemy_attack()


def enemy_attack():
    """Execute enemy attack in combat"""
    game = st.session_state.game
    
    if not game.in_combat or game.game_over or not game.enemy:
        return
    
    if game.fighting_boss:
        enemy = st.session_state.bosses[game.floor]
    else:
        enemy = game.enemy
    
    enemy_power = enemy["strength"]
    enemy_agility = enemy.get("agility", 5)
    
    # Evasion chance
    evasion_chance = max(0.05, (game.agility - enemy_agility) / 100)
    if random.random() < evasion_chance:
        game.message_log.append("You evaded the enemy's attack!")
        return
    
    damage = max(1, enemy_power - (game.agility // 3))
    game.health -= damage
    game.message_log.append(f"Enemy hits you for {damage} damage.")
    
    if game.health <= 0:
        game.health = 0
        game.game_over = True
        game.message_log.append("You died. Game over.")


def start_game(chosen_class):
    """Initialize game state for new game"""
    classes = st.session_state.classes
    stats = classes[chosen_class]
    
    game = GameState()
    game.player_class = chosen_class
    game.player_image = stats["image_url"]
    game.health = stats["health"]
    game.max_health = stats["health"]
    game.mana = stats["mana"]
    game.max_mana = stats["mana"]
    game.strength = stats["strength"]
    game.agility = stats["agility"]
    
    game.message_log = [
        st.session_state.floor_story[1],
        f"You chose {chosen_class}. {stats['description']} Enjoy!"
    ]
    
    st.session_state.game = game


def solve_puzzle(answer):
    """Validate puzzle solution and handle results"""
    game = st.session_state.game
    puzzles = st.session_state.puzzles
    
    if not game.in_puzzle or game.floor not in puzzles:
        return
    
    correct = puzzles[game.floor]["answer"]
    if answer.strip().lower() == correct:
        game.solved_puzzles.add(game.floor)
        game.puzzle_solved = True
        game.in_puzzle = False
        game.message_log.append("Puzzle solved! You may proceed.")
        game.skill_points += st.session_state.base_skill_points
        game.pending_skill_points = True
        try_encounter()
    else:
        game.message_log.append("Wrong answer, try again.")
        game.in_combat = False


def next_floor():
    """Advance player to next floor of the tower"""
    game = st.session_state.game
    max_floor = st.session_state.max_floor
    floor_story = st.session_state.floor_story
    
    if game.floor < max_floor:
        game.floor += 1
        game.enemies_defeated = 0
        game.message_log.append(f"You advance to floor {game.floor}.")
        game.message_log.append(floor_story[game.floor])
        game.in_combat = False
        game.enemy = None
        game.enemy_health = 0
        game.in_puzzle = False
        game.puzzle_solved = False
        game.fighting_boss = False
    else:
        game.message_log.append("You have reached the top of the tower!")
        game.game_over = True


def try_encounter():
    """Attempt to trigger random encounter"""
    game = st.session_state.game
    puzzles = st.session_state.puzzles
    enemies = st.session_state.enemies
    
    if game.in_combat or game.game_over or game.in_puzzle:
        return
    
    if (game.floor not in game.solved_puzzles and 
        random.random() < 0.3 and 
        game.floor in puzzles):
        encounter.start_puzzle(game, puzzles)
    else:
        encounter.encounter_enemy(game, next_floor, st.session_state.max_floor, enemies, random)


def cast_spell():
    """Cast spells in combat"""
    game = st.session_state.game
    
    if not game.in_combat or game.game_over:
        return
    
    if game.mana >= 20:
        game.mana -= 20
        base_damage = game.strength + 10
        damage = max(1, base_damage - random.randint(0, 5))
        game.enemy_health -= damage
        game.message_log.append(f"You cast a spell dealing {damage} damage!")
        
        if game.enemy_health <= 0:
            general.handle_victory(game, encounter, st.session_state.bosses, st.session_state.base_skill_points)
        else:
            enemy_attack()
    else:
        game.message_log.append("Not enough mana to cast a spell!")


def rest():
    """Rest to recover health and mana"""
    game = st.session_state.game
    
    if game.in_combat or game.game_over or game.in_puzzle:
        return
    
    heal_amount = min(30, game.max_health - game.health)
    mana_amount = min(30, game.max_mana - game.mana)
    
    game.health += heal_amount
    game.mana += mana_amount
    game.message_log.append(f"You rest and recover {heal_amount} HP and {mana_amount} mana.")
    try_encounter()


def main():
    st.set_page_config(page_title="D&D Tower Adventure", layout="wide")
    
    # Load game data
    if 'classes' not in st.session_state:
        with open('dnd_game_data.json', 'r') as f:
            game_data = json.load(f)
        
        st.session_state.classes = game_data['CLASSES']
        st.session_state.enemies = {int(k): v for k, v in game_data['ENEMIES'].items()}
        st.session_state.bosses = {int(k): v for k, v in game_data['BOSSES'].items()}
        st.session_state.puzzles = {int(k): v for k, v in game_data['PUZZLES'].items()}
        st.session_state.floor_story = {int(k): v for k, v in game_data['FLOOR_STORY'].items()}
        st.session_state.max_floor = 10
        st.session_state.base_skill_points = 5
    
    # Initialize game state
    if 'game' not in st.session_state:
        st.session_state.game = GameState()
        st.session_state.game.message_log = [st.session_state.floor_story[0]]
    
    game = st.session_state.game
    
    # Title
    st.title("🏰 D&D Tower Adventure")
    
    # Class selection screen
    if not game.player_class:
        show_class_selection()
    else:
        show_game_interface()


def show_class_selection():
    """Display class selection screen"""
    st.header("Choose Your Starter Class")
    classes = st.session_state.classes
    
    # Load saved games section
    save_files = list_save_files()
    if save_files:
        with st.expander("📂 Load Saved Game", expanded=False):
            st.write("Available save files:")
            for save_file in save_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(save_file)
                with col2:
                    if st.button("Load", key=f"load_{save_file}"):
                        if save_file.endswith('.json'):
                            load_game_from_json(save_file)
                        else:
                            load_game_from_pickle(save_file)
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_{save_file}"):
                        try:
                            os.remove(save_file)
                            st.success(f"Deleted {save_file}")
                            st.rerun()
                        except:
                            st.error(f"Error deleting {save_file}")
    
    st.markdown("---")
    st.subheader("New Game")
    
    cols = st.columns(3)
    for i, (c, info) in enumerate(classes.items()):
        with cols[i]:
            st.subheader(c)
            st.image(info["image_url"], width=200)
            st.write(info["description"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"❤️ {info['health']} HP")
                st.write(f"💪 {info['strength']} STR")
            with col2:
                st.write(f"🔵 {info['mana']} MP")
                st.write(f"⚡ {info['agility']} AGI")
            
            if st.button(f"Select {c}", key=f"select_{c}"):
                start_game(c)
                st.rerun()


def show_game_interface():
    """Display main game interface"""
    game = st.session_state.game
    classes = st.session_state.classes
    
    # Sidebar - Player Stats
    with st.sidebar:
        st.header(f"🏃 {game.player_class}")
        st.image(game.player_image, width=200)
        
        st.subheader("Stats")
        st.progress(game.health / game.max_health, 
                   text=f"❤️ HP: {game.health}/{game.max_health}")
        st.progress(game.mana / game.max_mana,
                   text=f"🔵 MP: {game.mana}/{game.max_mana}")
        
        st.write(f"💪 Strength: {game.strength}")
        st.write(f"⚡ Agility: {game.agility}")
        st.write(f"⭐ Skill Points: {game.skill_points}")
        st.write(f"🏆 Floor: {game.floor}/10")
        
        # Save/Load buttons
        st.markdown("---")
        st.subheader("💾 Save/Load")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save JSON"):
                save_game_to_json()
                st.rerun()
        with col2:
            if st.button("💾 Save Pickle"):
                save_game_to_pickle()
                st.rerun()
        
        if st.button("🔄 New Game"):
            game.reset()
            game.message_log = [st.session_state.floor_story[0]]
            st.rerun()
        
        # Show last save time if available
        if game.save_timestamp:
            try:
                save_time = datetime.datetime.fromisoformat(game.save_timestamp)
                st.caption(f"Last save: {save_time.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                pass
    
    # Main area
    if game.game_over:
        show_game_over()
    else:
        show_game_log()
        
        if game.pending_skill_points and game.skill_points > 0:
            show_skill_distribution()
        elif game.in_combat:
            show_combat_interface()
        elif game.in_puzzle:
            show_puzzle_interface()
        else:
            show_exploration_interface()


def show_game_over():
    """Display game over screen"""
    game = st.session_state.game
    
    if game.health <= 0:
        st.error("💀 You died! Game Over.")
    else:
        st.success("🎉 You conquered the tower! You win!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Play Again"):
            game.reset()
            game.message_log = [st.session_state.floor_story[0]]
            st.rerun()
    with col2:
        if st.button("💾 Save Final State"):
            save_game_to_json()
            st.rerun()


def show_game_log():
    """Display game message log"""
    game = st.session_state.game
    
    st.subheader("📜 Game Log")
    log_container = st.container(height=300)
    
    with log_container:
        for msg in reversed(game.message_log[-10:]):
            if msg.startswith("![Boss]("):
                st.image(msg.split("(")[1].split(")")[0], width=200)
            else:
                st.write(msg)


def show_skill_distribution():
    """Display skill point distribution interface"""
    game = st.session_state.game
    
    with st.expander("⭐ Distribute Skill Points", expanded=True):
        st.write(f"Available points: {game.skill_points}")
        
        hp_points = st.number_input("Health (+10 per point)", 0, game.skill_points, 0)
        mana_points = st.number_input("Mana (+10 per point)", 0, game.skill_points, 0)
        str_points = st.number_input("Strength", 0, game.skill_points, 0)
        agi_points = st.number_input("Agility", 0, game.skill_points, 0)
        
        if st.button("Apply Points"):
            if apply_skill_points(hp_points, mana_points, str_points, agi_points):
                st.rerun()


def show_combat_interface():
    """Display combat interface"""
    game = st.session_state.game
    classes = st.session_state.classes
    
    st.subheader(f"⚔️ Combat with {game.enemy['name']}")
    
    if "image url" in game.enemy:
        st.image(game.enemy["image url"], width=200)
    
    st.progress(game.enemy_health / game.enemy['health'], 
               text=f"Enemy Health: {game.enemy_health}/{game.enemy['health']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚔️ Basic Attack"):
            player_attack()
            st.rerun()
        if st.button("✨ Cast Spell (20 MP)"):
            cast_spell()
            st.rerun()
    
    with col2:
        if st.button("🛡️ Guard"):
            game.message_log.append("You raise your guard!")
            enemy_attack()
            st.rerun()
    
    st.markdown("---")
    st.subheader("🎯 Class Skills")
    
    class_skills = classes[game.player_class]["skills"]
    for skill, details in class_skills.items():
        if st.button(f"{skill} ({details['cost']} MP)"):
            player_attack(skill)
            st.rerun()


def show_puzzle_interface():
    """Display puzzle interface"""
    game = st.session_state.game
    puzzles = st.session_state.puzzles
    
    st.subheader("🧩 Puzzle Encounter")
    st.image("https://media.tenor.com/Y2jZZeojXg8AAAAM/puzzle-angry.gif", width=200)
    
    puzzle = puzzles[game.floor]
    st.write(puzzle["question"])
    answer = st.text_input("Your answer:")
    
    if st.button("Submit Answer"):
        solve_puzzle(answer)
        st.rerun()


def show_exploration_interface():
    """Display exploration interface"""
    game = st.session_state.game
    
    st.subheader(f"🏰 Floor {game.floor}")
    st.write(st.session_state.floor_story.get(game.floor, ""))
    
    # Quick save button
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Explore", use_container_width=True):
            try_encounter()
            st.rerun()
    with col2:
        if st.button("💤 Rest", use_container_width=True):
            rest()
            st.rerun()
    with col3:
        if st.button("💾 Quick Save", use_container_width=True):
            save_game_to_json()
            st.rerun()


if __name__ == "__main__":
    main()