# pySnake

pySnake includes two classes, one for game and one for simple bot.
 - `snake_game()`, `snake_bot()`

Dependencies:
 - PyGame

To run: 
 - Run file `main.py`
   - This will run the game with the bot enabled.
   - To disable the bot, `run_bot` can be set to `False` at the top of the file.

Minimum working example:
```python
pygame.init()
screen = pygame.display.set_mode((disp_width, disp_height))
pygame.display.set_caption("Snake by Duncan")
clock = pygame.time.Clock()

snek = snake_game(screen, disp_width, disp_height, speed, fps, scale)
bot = snake_bot(scale)

while True:
  snek.change_direction(bot.get_move(snek))
  snek.update_game()
  clock.tick(fps)
```
