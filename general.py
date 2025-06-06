
def init_game(session_state , floor,  ):
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
    
