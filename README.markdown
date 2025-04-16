# Realistic Snake Game

This is a modern implementation of the classic Snake game, built using Python, Pygame, and OpenGL for enhanced graphics. The game features a realistic snake with detailed textures, a grassy background, and various food types with unique appearances.

## Features

- **Realistic Graphics**: The snake has a detailed design with eyes, a tongue, and animated movements. The background is a textured grass field.
- **Multiple Food Types**: Includes apple, banana, strawberry, mouse, and paper, each with distinct textures. Food types cycle deterministically per game run (apple in first run, banana in second, etc.).
- **Dynamic Gameplay**:
  - Snake movement controlled with arrow keys.
  - Eating food increases the score (10 points for most foods, 20 for paper) and snake length.
  - Game ends after eating 50 food items or colliding with walls/self.
- **Animations**:
  - Eating animation scales the snake's head.
  - Game over animation with a shaking effect and fading snake.
- **Sound Effects**: Optional beep for eating and game over sound (requires `beep.wav` and `gameover.wav` files).
- **Score Tracking**: Displays "Food Eaten: X/50" on-screen.

## Requirements

- Python 3.6+
- Pygame (`pip install pygame`)
- PyOpenGL (`pip install PyOpenGL PyOpenGL_accelerate`)
- NumPy (`pip install numpy`)

## Installation

1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install pygame PyOpenGL PyOpenGL_accelerate numpy
   ```
3. Place optional sound files (`beep.wav`, `gameover.wav`) in the same directory as the script, or the game will run without sound.

## How to Run

1. Save the game code as `snake_game.py`.
2. Run the script:
   ```bash
   python snake_game.py
   ```

## Controls

- **Arrow Keys**: Move the snake up, down, left, or right.
- **Enter**: Restart the game after game over.
- **Q**: Quit the game when in game over state.

## Game Mechanics

- The snake moves continuously in the current direction at a fixed speed.
- Food appears at random grid positions, avoiding the snake’s body.
- The game ends if:
  - The snake hits the grid boundaries (20x20 grid).
  - The snake collides with itself.
  - 50 food items are eaten (win condition).
- Each game run uses a specific food type (apple, banana, strawberry, mouse, paper) based on the run count, resetting to apple when quitting.

## Customization

- **Snake Color**: Modify the `draw_snake` function to change RGB color tuples for the head, body, and tail.
- **Speed**: Adjust the `SPEED` constant (default 0.15 seconds per move) for faster or slower gameplay.
- **Grid Size**: Change `GRID_SIZE` (default 20) and `WIN_SIZE` (default 800x600) for a different play area.
- **Food Types**: Edit `food_types` list and corresponding texture functions to add/remove food items.

## Known Issues

- Sound files are optional; missing files are handled gracefully but produce no sound.
- High grid sizes with small window sizes may cause rendering issues due to cell size calculations.
- No pause feature currently implemented.

## Future Improvements

- Add a pause/resume feature (e.g., with `P` key).
- Implement dynamic snake color changes (e.g., random colors per game or on food eaten).
- Add a main menu and difficulty settings.
- Support for additional food effects (e.g., speed boost, reverse direction).

## License

This project is open-source and available under the MIT License.