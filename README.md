# pySnake

To run: use file `main.py`

Includes two classes, one for game and one for simple bot.
`snake_game()`, `snake_bot()`

After creation, update `snake_game()` object on every frame with `snake_game.update_game()`

Change direction of snake by using:

`snake_game.change_direction("up/down/left/right")`

Bot can be directly queried for moves using the above command with:

`snake_game.change_direction(snake_bot.get_move(snake_game))`
