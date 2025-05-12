# Simple DnD Game - Stats in Combat

This is a simple Dungeons and Dragons style game implemented using Streamlit. Players choose a class, explore floors of a tower, encounter enemies and puzzles, and try to reach the top!

## Features

* **Class Selection:** Choose from three distinct classes: Knight, Mage, and Shadow, each with unique starting stats and descriptions.
* **Turn-Based Gameplay:** Engage in combat with enemies using an attack action. Mages can also cast spells using mana.
* **Floor Progression:** Explore different floors of a tower, each with unique encounters and a flavor text.
* **Enemy Encounters:** Battle various enemies with different health, strength, and agility.
* **Puzzles:** Test your wit by solving riddles to progress.
* **Boss Battles:** Face powerful bosses at the end of certain floors.
* **Skill Point System:** Earn skill points after defeating enemies or solving puzzles and allocate them to improve your health, mana, strength, and agility.
* **Game Over:** The game ends if your health reaches zero.
* **Victory:** Reach the top floor of the tower to win!
* **Game Log:** A running log of game events keeps you informed.
* **Resting:** Outside of combat and puzzles, you can rest to recover some health and mana.

## How to Run

1.  **Install Streamlit:**
    ```bash
    pip install streamlit
    ```

2.  **Save the Code:** Save the provided Python code as a `.py` file (e.g., `dnd_game.py`).

3.  **Run the Game:** Open your terminal or command prompt, navigate to the directory where you saved the file, and run:
    ```bash
    streamlit run dnd_game.py
    ```

    This will automatically open the game in your web browser.

## Gameplay

1.  **Choose Your Class:** On the initial screen, select your preferred class by clicking the "Select" button below its description.
2.  **Explore:** On each floor, you'll have an "Explore" button. Click it to trigger a random encounter, which could be an enemy or a puzzle.
3.  **Combat:**
    * When an enemy appears, you'll see its health.
    * Use the "Attack" button to deal damage based on your strength.
    * If you are a Mage (or have enough mana), you can use the "Cast Spell" button for a more powerful attack that consumes mana.
    * The enemy will also attack you each turn.
    * Defeat the enemy to earn skill points and proceed.
4.  **Puzzles:**
    * If you encounter a puzzle, the question will be displayed.
    * Type your answer in the "Your answer:" field and click "Submit Answer".
    * Solving the puzzle correctly will grant you skill points and allow you to move to the next floor.
5.  **Skill Points:**
    * After defeating an enemy or solving a puzzle, you'll receive skill points.
    * A "Distribute Skill Points" section will appear, allowing you to allocate points to increase your stats (Health, Mana, Strength, Agility).
    * Enter the number of points you want to add to each stat and click "Apply skill points".
6.  **Resting:** When you are not in combat or solving a puzzle, you can click the "Rest" button to recover some health and mana. This might trigger another encounter afterwards.
7.  **Progression:** Continue exploring floors, battling enemies, and solving puzzles until you reach the top floor or your health drops to zero.

## Game Mechanics

* **Health:** Your character's hit points. If it reaches 0, the game is over.
* **Mana:** A resource used by Mages to cast spells.
* **Strength:** Determines the base damage of your regular attacks.
* **Agility:** Affects your chance to score a critical hit and your chance to evade enemy attacks.
* **Critical Hit:** A lucky attack that deals extra damage.
* **Evasion:** A chance to completely avoid an enemy's attack.
* **Skill Points:** Points earned after overcoming challenges, used to improve your character's stats.

## Future Enhancements

* More character classes and abilities.
* A more complex combat system with different attack types and special skills.
* More diverse enemies and bosses with unique abilities.
* More intricate puzzles and story elements.
* Items and equipment to enhance character stats.
* Saving and loading game progress.

