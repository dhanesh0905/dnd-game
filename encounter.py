def encounter_enemy(session_state, nextfloor, maxfloor ,ENEMIES , random ):
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

def start_boss(session_state , bosses ):
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
    puzzle = PUZZLE.get(session_state.floor)
    if puzzle and session_state.floor not in session_state.solved_puzzles:
        session_state.in_puzzle = True
        session_state.puzzle_solved = False
        session_state.message_log.append("You encounter a puzzle!")
    else:
        session_state.in_puzzle = False