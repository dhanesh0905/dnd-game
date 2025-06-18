
def init_game(session_state , floor, ):
    """
    Initializes the game state with default values for a new game session.

    Sets up player attributes, combat status, puzzle status, and game progress trackers.
    The starting floor number is recorded in the message log.

    Parameters:
    session_state (dict): The game state dictionary to initialize
    floor (int): Starting floor number (recorded in message log)
    """
    session_state.update(
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
        message_log=[floor],
        game_over=False,
        skill_points=0,
        pending_skill_points=False,
        fighting_boss=False,
        solved_puzzles=set(),
        enemies_defeated=0,
        defeated_enemies=set(),
        encountered_by_floor={},
    )
    
    
"""
    Advances the player to the next floor and updates game state accordingly.

    Resets combat/puzzle states, appends progression messages to the log, and handles
    game completion when reaching the maximum floor. Boss status is cleared upon advancement.

    Parameters:
    session_state (dict): Current game state to modify
    floor_story (dict): Mapping of floor numbers to their introductory story text
    MAX_FLOOR (int): Highest possible floor number (top of tower)
    """
def next_floor(session_state, floor_story, MAX_FLOOR):
    
    if session_state.floor < MAX_FLOOR:
        session_state.floor += 1
        session_state.enemies_defeated = 0
        session_state.message_log.append(f"You advance to floor {session_state.floor}.")
        session_state.message_log.append(floor_story[session_state.floor])
        session_state.in_combat = False
        session_state.enemy = None
        session_state.enemy_health = 0
        session_state.in_puzzle = False
        session_state.puzzle_solved = False
        session_state.fighting_boss = False
    else:
        session_state.message_log.append("You have reached the top of the tower!")
        session_state.game_over = True
        
        
        
"""
    Processes victory outcomes after defeating an enemy.

    Updates defeat trackers, awards skill points, triggers boss encounters when conditions
    are met, and prepares for skill point allocation. Handles both regular and boss victories.

    Parameters:
    session_state (dict): Game state to update
    encounter (object): Encounter controller with start_boss() method
    bosses (dict): Boss data for current floor
    BASE_SKILL_POINTS (int): Base skill points awarded for regular enemies (doubled for bosses)
    """
def handle_victory(session_state, encounter , bosses, BASE_SKILL_POINTS):

    enemy_name = session_state.enemy['name']
    session_state.defeated_enemies.add(enemy_name)
    
    if session_state.fighting_boss:
        session_state.message_log.append(f"You defeated the boss {enemy_name}!")
        session_state.skill_points += BASE_SKILL_POINTS * 2
        session_state.fighting_boss = False
        next_floor()
    else:
        session_state.message_log.append(f"You defeated the {enemy_name}!")
        session_state.enemies_defeated += 1
        session_state.skill_points += BASE_SKILL_POINTS
        if session_state.enemies_defeated >= 3:
            encounter.start_boss(session_state, bosses )

    session_state.pending_skill_points = True
    session_state.in_combat = False
    session_state.enemy = None
    session_state.enemy_health = 0