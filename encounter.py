def encounter_enemy(session_state, nextfloor, maxfloor, ENEMIES, random):
    """
    Attempts to trigger a random encounter on the current floor.
    
    There's a 70% chance to attempt an encounter. If triggered, selects a random 
    non-defeated enemy not previously encountered on this floor. If no enemies are 
    available, either progresses to the next floor or triggers game completion.

    Parameters:
        session_state (State): Current game state object containing:
            - floor (int): Current floor number
            - defeated_enemies (set): Names of defeated enemies
            - encountered_by_floor (dict): Map of floor → set of encountered enemy names
            - message_log (list): Game message buffer
            - game_over (bool): Win/lose state flag
        nextfloor (function): Callback to advance to next floor
        maxfloor (int): Highest floor number in the game
        ENEMIES (dict): Floor → list of enemy definitions
        random (module): Random number generator module

    Returns:
        bool: True if encounter triggered, False otherwise
    """
    if random.random() < 0.7:  
        enemy_list = ENEMIES.get(session_state.floor, [])
        
        if not enemy_list:
            return False
        session_state.encountered_by_floor.setdefault(session_state.floor, set())

        available_enemies = [
            e for e in enemy_list 
            if e['name'] not in session_state.defeated_enemies 
            and e['name'] not in session_state.encountered_by_floor[session_state.floor]
        ]

        if not available_enemies:
            if session_state.floor < maxfloor:
                session_state.message_log.append("No more new enemies on this floor. Moving to next floor.")
                nextfloor()
                return False
            else:
                session_state.message_log.append("All enemies defeated! You win!")
                session_state.game_over = True
                return False

        enemy = random.choice(available_enemies)
        session_state.enemy = enemy
        session_state.enemy_health = enemy["health"]
        session_state.in_combat = True
        session_state.message_log.append(f"A wild {enemy['name']} appears!")
        session_state.encountered_by_floor[session_state.floor].add(enemy['name'])
        return True
    return False


def start_boss(session_state, bosses):
    """
    Triggers a boss encounter if the current floor has a boss and not already defeated.
    
    Updates game state to enter combat with the floor's boss. Adds descriptive messages
    including any boss image URL to the message log.

    Parameters:
        session_state (State): Current game state object containing:
            - floor (int): Current floor number
            - message_log (list): Game message buffer
        bosses (dict): Floor → boss definition dictionary
    """
    if session_state.floor in bosses:
        boss = bosses[session_state.floor]
        session_state.fighting_boss = True
        session_state.in_combat = True
        session_state.enemy = boss
        session_state.enemy_health = boss["health"]
        session_state.message_log.append(f"Boss {boss['name']} appears! {boss.get('description','')}")
        if "image url" in boss:
            session_state.message_log.append(f"![Boss]({boss['image url']})")


def start_puzzle(session_state, PUZZLE):
    """
    Initiates a puzzle encounter if the current floor has an unsolved puzzle.
    
    Updates game state to enter puzzle mode. Skips if puzzle already solved.

    Parameters:
        session_state (State): Current game state object containing:
            - floor (int): Current floor number
            - solved_puzzles (set): Floors with completed puzzles
            - message_log (list): Game message buffer
        PUZZLE (dict): Floor → puzzle definition dictionary
    """
    puzzle = PUZZLE.get(session_state.floor)
    if puzzle and session_state.floor not in session_state.solved_puzzles:
        session_state.in_puzzle = True
        session_state.puzzle_solved = False
        session_state.message_log.append("You encounter a puzzle!")
    else:
        session_state.in_puzzle = False