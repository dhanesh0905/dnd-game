"""
Imports:
    json: For loading game data and serialization
    streamlit (st): For creating the web UI
    random: For game randomization
    general: Custom game utility functions
    encounter: Custom encounter handling functions
    datetime: for saving game state with timestamps
    sqlite3: For database operations
"""
import json
import streamlit as st
import random
import general
import encounter
import datetime
import sqlite3
import os
from contextlib import closing


# Loading the game from the json file 
with open('dnd_game_data.json', 'r') as f:
    game_data = json.load(f)


CLASSES = game_data['CLASSES']
ENEMIES = {int(k): v for k, v in game_data['ENEMIES'].items()}
BOSSES = {int(k): v for k, v in game_data['BOSSES'].items()}
PUZZLES = {int(k): v for k, v in game_data['PUZZLES'].items()}
FLOOR_STORY = {int(k): v for k, v in game_data['FLOOR_STORY'].items()}

MAX_FLOOR = 10
BASE_SKILL_POINTS = 5


class GameDatabase:
    """SQLite database handler for game persistence"""
    
    def __init__(self, db_name="dnd_game.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            
            # Create saves table
            cursor.execute("""
                CREATES TABLE IF NOT EXISTS game_saves (id INTEGER PRIMARY KEY AUTOINCREMENT,save_name TEXT NOT NULL,player_class TEXT,player_image TEXT,health INTEGER,max_health INTEGER,mana INTEGER,max_mana INTEGER,strength INTEGER,agility INTEGER,
                    floor INTEGER,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            
            # Create combat_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS combat_logs ( id INTEGER PRIMARY KEY AUTOINCREMENT,save_id INTEGER, floor INTEGER, enemy_name TEXT,action TEXT,damage INTEGER,player_health INTEGER, enemy_health INTEGER,timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (save_id) REFERENCES game_saves(id) ON DELETE CASCADE)""")
            
            # Create achievements table
            cursor.execute("""CREATE TABLE IF NOT EXISTS achievements (id INTEGER PRIMARY KEY AUTOINCREMENT,save_id INTEGER,achievement_type TEXT,achievement_name TEXT,description TEXT, unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (save_id) REFERENCES game_saves(id) ON DELETE CASCADE)""")
            
            conn.commit()
    
    def save_game(self, save_name, session_state):
        """Save game state to database"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            
            # Convert sets to JSON strings for storage
            solved_puzzles_json = json.dumps(list(session_state.solved_puzzles))
            defeated_enemies_json = json.dumps(list(session_state.defeated_enemies))
            encountered_by_floor_json = json.dumps(session_state.encountered_by_floor)
            message_log_json = json.dumps(session_state.message_log)
            enemy_json = json.dumps(session_state.enemy) if session_state.enemy else '{}'
            
            # Check if save already exists
            cursor.execute("SELECT id FROM game_saves WHERE save_name = ?", (save_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing save
                cursor.execute(
                    , (
                    session_state.player_class,
                    session_state.player_image,
                    session_state.health,
                    session_state.max_health,
                    session_state.mana,
                    session_state.max_mana,
                    session_state.strength,
                    session_state.agility,
                    session_state.floor,
                    session_state.skill_points,
                    1 if session_state.pending_skill_points else 0,
                    1 if session_state.in_combat else 0,
                    enemy_json,
                    session_state.enemy_health,
                    1 if session_state.in_puzzle else 0,
                    1 if session_state.puzzle_solved else 0,
                    message_log_json,
                    1 if session_state.game_over else 0,
                    1 if session_state.fighting_boss else 0,
                    solved_puzzles_json,
                    session_state.enemies_defeated,
                    defeated_enemies_json,
                    encountered_by_floor_json,
                    save_name
                ))
                save_id = existing[0]
            else:
                # Insert new save
                cursor.execute(, (
                    save_name,
                    session_state.player_class,
                    session_state.player_image,
                    session_state.health,
                    session_state.max_health,
                    session_state.mana,
                    session_state.max_mana,
                    session_state.strength,
                    session_state.agility,
                    session_state.floor,
                    session_state.skill_points,
                    1 if session_state.pending_skill_points else 0,
                    1 if session_state.in_combat else 0,
                    enemy_json,
                    session_state.enemy_health,
                    1 if session_state.in_puzzle else 0,
                    1 if session_state.puzzle_solved else 0,
                    message_log_json,
                    1 if session_state.game_over else 0,
                    1 if session_state.fighting_boss else 0,
                    solved_puzzles_json,
                    session_state.enemies_defeated,
                    defeated_enemies_json,
                    encountered_by_floor_json
                ))
                save_id = cursor.lastrowid
            
            # Log combat action if in combat
            if session_state.in_combat and session_state.enemy:
                cursor.execute(
                    , (
                    save_id,
                    session_state.floor,
                    session_state.enemy.get('name', 'Unknown'),
                    session_state.health,
                    session_state.enemy_health
                ))
            
            # Check for achievements
            self.check_achievements(cursor, save_id, session_state)
            
            conn.commit()
            
            # Update session state with save info
            if hasattr(session_state, 'save_info'):
                session_state.save_info = {'id': save_id, 'name': save_name}
            
            return save_id
    
    def check_achievements(self, cursor, save_id, session_state):
        """Check and record achievements"""
        achievements = []
        
        # Floor progression achievements
        if session_state.floor >= 5:
            achievements.append(('floor', 'Tower Explorer', 'Reached floor 5'))
        if session_state.floor >= 10:
            achievements.append(('floor', 'Tower Master', 'Reached floor 10'))
        
        # Combat achievements
        if len(session_state.defeated_enemies) >= 10:
            achievements.append(('combat', 'Monster Slayer', 'Defeated 10 enemies'))
        
        # Puzzle achievements
        if len(session_state.solved_puzzles) >= 5:
            achievements.append(('puzzle', 'Puzzle Master', 'Solved 5 puzzles'))
        
        # Boss achievements
        if session_state.fighting_boss and session_state.enemy_health <= 0:
            boss_name = session_state.enemy.get('name', 'Boss')
            achievements.append(('boss', f'Slayer of {boss_name}', f'Defeated {boss_name}'))
        
        # Save achievements
        for achievement_type, name, description in achievements:
            cursor.execute(
                , (save_id, achievement_type, name, description, save_id, name))
    
    def load_game(self, save_name):
        """Load game state from database"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM game_saves WHERE save_name = ?", (save_name,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            save_data = dict(zip(columns, row))
            
            # Parse JSON fields
            save_data['solved_puzzles'] = set(json.loads(save_data['solved_puzzles'] or '[]'))
            save_data['defeated_enemies'] = set(json.loads(save_data['defeated_enemies'] or '[]'))
            save_data['encountered_by_floor'] = json.loads(save_data['encountered_by_floor'] or '{}')
            save_data['message_log'] = json.loads(save_data['message_log'] or '[]')
            
            # Parse enemy data
            enemy_data = json.loads(save_data['enemy'] or '{}')
            save_data['enemy'] = enemy_data if enemy_data else None
            
            # Convert boolean fields
            bool_fields = ['pending_skill_points', 'in_combat', 'in_puzzle', 
                          'puzzle_solved', 'game_over', 'fighting_boss']
            for field in bool_fields:
                save_data[field] = bool(save_data[field])
            
            return save_data
    
    def delete_game(self, save_name):
        """Delete a saved game"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM game_saves WHERE save_name = ?", (save_name,))
            conn.commit()
            return cursor.rowcount > 0
    
    def list_saves(self):
        """List all saved games"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            cursor.execute()
            return cursor.fetchall()
    
    def get_achievements(self, save_name):
        """Get achievements for a saved game"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            cursor.execute(, (save_name,))
            return cursor.fetchall()
    
    def get_combat_history(self, save_name, limit=10):
        """Get combat history for a saved game"""
        with closing(sqlite3.connect(self.db_name)) as conn:
            cursor = conn.cursor()
            cursor.execute(, (save_name, limit))
            return cursor.fetchall()


# Initialize database
db = GameDatabase()


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
    
    # Save game after applying points
    if hasattr(st.session_state, 'current_save_name'):
        db.save_game(st.session_state.current_save_name, st.session_state)
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
    msg = f"You use {skill} and deal {damage} damage!" if skill else f"You dealt {damage} damage"
    if crit:
        msg += " (Critical hit!)"
    st.session_state.message_log.append(msg)

    if st.session_state.enemy_health <= 0:
        general.handle_victory(st.session_state, encounter, BOSSES, BASE_SKILL_POINTS)
        if hasattr(st.session_state, 'current_save_name'):
            db.save_game(st.session_state.current_save_name, st.session_state)
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
    
    # Ask for save name
    save_name = st.text_input("Enter a name for your save file:", 
                              value=f"{chosen_class}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    if save_name:
        st.session_state.current_save_name = save_name
        db.save_game(save_name, st.session_state)
        st.session_state.message_log.append(f"Game saved as: {save_name}")


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
        if hasattr(st.session_state, 'current_save_name'):
            db.save_game(st.session_state.current_save_name, st.session_state)


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
        if hasattr(st.session_state, 'current_save_name'):
            db.save_game(st.session_state.current_save_name, st.session_state)
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
        if hasattr(st.session_state, 'current_save_name'):
            db.save_game(st.session_state.current_save_name, st.session_state)
    else:
        st.session_state.message_log.append("You have reached the top of the tower!")
        st.session_state.game_over = True
        if hasattr(st.session_state, 'current_save_name'):
            db.save_game(st.session_state.current_save_name, st.session_state)


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
            if hasattr(st.session_state, 'current_save_name'):
                db.save_game(st.session_state.current_save_name, st.session_state)
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
    if hasattr(st.session_state, 'current_save_name'):
        db.save_game(st.session_state.current_save_name, st.session_state)
    try_encounter()


# Initialize game state
if "player_class" not in st.session_state:
    general.init_game(st.session_state, FLOOR_STORY[0])


# Class selection screen
if not st.session_state.player_class:
    st.header("Choose Your Starter Class")
    
    # Load saved games section
    saves = db.list_saves()
    if saves:
        with st.expander("📂 Load Saved Game", expanded=False):
            st.write("Available save files:")
            for save in saves:
                save_name, player_class, floor, created_at, updated_at = save
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{save_name}**")
                    st.caption(f"Class: {player_class} | Floor: {floor}")
                    st.caption(f"Last played: {updated_at[:19]}")
                with col2:
                    if st.button("Load", key=f"load_{save_name}"):
                        save_data = db.load_game(save_name)
                        if save_data:
                            # Update session state
                            for key, value in save_data.items():
                                if key not in ['id', 'save_name', 'created_at', 'updated_at']:
                                    st.session_state[key] = value
                            st.session_state.current_save_name = save_name
                            st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_{save_name}"):
                        if db.delete_game(save_name):
                            st.success(f"Deleted save: {save_name}")
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
    
    # Database section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Database")
    
    if hasattr(st.session_state, 'current_save_name'):
        st.sidebar.write(f"Save: {st.session_state.current_save_name}")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("💾 Save"):
                db.save_game(st.session_state.current_save_name, st.session_state)
                st.sidebar.success("Game saved!")
                st.rerun()
        with col2:
            if st.button("📊 Stats"):
                # Show achievements
                achievements = db.get_achievements(st.session_state.current_save_name)
                if achievements:
                    st.sidebar.subheader("🏆 Achievements")
                    for name, desc, unlocked in achievements:
                        st.sidebar.write(f"**{name}**: {desc}")
    
    # Game over screen
    if st.session_state.game_over:
        st.error("💀 You died! Game Over." if st.session_state.health <= 0 else "🎉 You conquered all floors! You win!")
        
        # Show final statistics
        if hasattr(st.session_state, 'current_save_name'):
            achievements = db.get_achievements(st.session_state.current_save_name)
            combat_history = db.get_combat_history(st.session_state.current_save_name, 5)
            
            with st.expander("📊 Final Statistics"):
                st.write(f"**Final Floor**: {st.session_state.floor}")
                st.write(f"**Enemies Defeated**: {len(st.session_state.defeated_enemies)}")
                st.write(f"**Puzzles Solved**: {len(st.session_state.solved_puzzles)}")
                
                if achievements:
                    st.subheader("🏆 Achievements Unlocked")
                    for name, desc, unlocked in achievements:
                        st.write(f"• **{name}**: {desc}")
                
                if combat_history:
                    st.subheader("⚔️ Recent Combat History")
                    for combat in combat_history:
                        floor, enemy, action, damage, player_hp, enemy_hp, timestamp = combat
                        st.write(f"Floor {floor}: vs {enemy} - Player HP: {player_hp}, Enemy HP: {enemy_hp}")
        
        if st.button("Restart"):
            general.init_game(st.session_state, FLOOR_STORY[0])
            if hasattr(st.session_state, 'current_save_name'):
                del st.session_state.current_save_name
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
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Explore"):
                            try_encounter()
                            st.rerun()
                    with col2:
                        if st.button("Rest"):
                            rest()
                            st.rerun()
                else:
                    st.success("Congratulations! You've conquered the tower!")
                    if st.button("Play Again"):
                        general.init_game(st.session_state, FLOOR_STORY[0])