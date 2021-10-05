import pygame
from time import time
from random import randrange

disp_height = 1000
disp_width = 1000
fps = 60 #does not affect speed.
scale = 10 #size of pixels. Decreases speed.
speed = 500
run_bot = True

class snake_game():
    def __init__(self, pygame_screen, width, height, speed, frames_per_second, size_multiplier):
        #screen properties
        self.screen = pygame_screen
        self.screen_height = height
        self.screen_width = width
        self.scale = size_multiplier
        self.color_dict = {
            "background": (0, 0, 80),
            "snake": (204, 204, 255),
            "text": (255, 255, 255)
        }

        # initialize background
        self.screen.fill(self.color_dict["background"])
        self.removed_pixel = []

        #initialize timers
        self.frame_time = 1 / frames_per_second
        self.last_time = 0
        self.current_time = time()
        self.time_since_last_move = 0

        #Snake properties
        self.speed = speed #pixels per second
        self.length = 1
        self.direction = (0, 0) #x/y tuple for direction
        self.coord_dict = [(width//2, height//2)] #0 is tail, end is head
        self.buffer = False

        #food properties
        self.food_x = 0
        self.food_y = 0
        self.generate_food()

    #Function to generate new location for next food. Ensures that location is not ON player
    def generate_food(self):
        #regenerates until it finds somewhere not on the snake
        # Can add other conditions later if needed
        while True:
            x = int(randrange(self.scale + 1, self.screen_width-self.scale-1))
            y = int(randrange(self.scale + 1, self.screen_height-self.scale-1))
            if not (x, y) in self.coord_dict:
                break
        self.food_x = x
        self.food_y = y

    #Function to change directions. Only way of interacting with game.
    def change_direction(self, dir):
        #buffer variable stops consecutive inputs from happening, allowing function like in-place 180
        #locks input to 1 button press per frame, resets when frame timer in update_game() does
        if self.buffer == False:
            self.buffer = True
            if dir == "up":
                if self.direction[1] == 0: #prevents 180
                    self.direction = (0, -1)
            elif dir == "down":
                if self.direction[1] == 0: #prevents 180
                    self.direction = (0, 1)
            elif dir == "left":
                if self.direction[0] == 0: #prevents 180
                    self.direction = (-1, 0)
            elif dir == "right":
                if self.direction[0] == 0: #prevents 180
                    self.direction = (1, 0)

    #Mathematically move the snake, perform array operations, and more
    #Runs all collision checkers
    def move_snake(self):
        current_coord = self.coord_dict[len(self.coord_dict)-1]
        self.coord_dict.append((current_coord[0] + (self.direction[0]*self.scale), current_coord[1] + (self.direction[1]*self.scale)))

        #test for food collision, add to snake and regenerate food
        if self.test_collision("food"):
            self.length += 1
            self.removed_pixel.append((self.food_x, self.food_y))
            self.generate_food()

        #Clean up the back of the snake as it moves
        if len(self.coord_dict) > self.length:
            self.removed_pixel.append(self.coord_dict[0])
            self.coord_dict.pop(0)

        #test for self collision, immediate loss/quit
        if self.test_collision("self"):
            pygame.quit()

        #test for wall collision, immediate loss/quit
        if self.test_collision("wall"):
            pygame.quit()

    #Checks collision of all types against the head coordinate of the snake
    def test_collision(self, type):
        head_coord = self.coord_dict[len(self.coord_dict) - 1]
        x = head_coord[0]
        y = head_coord[1]

        if type == "food":
            #Tests food collision, gives buffer of size "scale" around the root coordinate.
            if (x <= self.food_x + self.scale - 1) and (x >= self.food_x - self.scale + 1) and (y <= self.food_y + self.scale - 1) and (y >= self.food_y - self.scale + 1):
                return True

        elif type == "self":
            #force skips self collision tests if snake is too short
            #was necessary in older versions. not sure if it is anymore. don't feel like tempting the devil today.
            if len(self.coord_dict) > 4:
                coord_copy = self.coord_dict[0:len(self.coord_dict) - 4]
            else:
                coord_copy = []
            if head_coord in coord_copy:
                return True

        elif type == "wall":
            #Tests for wall collision on edge touch.
            if (x < 0) or (x > self.screen_width - self.scale) or (y < 0) or (y > self.screen_height - self.scale):
                return True

        return False

    #Standardized function to draw x/y pixel a particular color
    def draw_pixel(self, x, y, color_code):
        pygame.draw.rect(self.screen, self.color_dict[color_code], (x,y,self.scale,self.scale))

    #Main game runner. Progresses game 1 tick every time it is run.
    def update_game(self):
        self.current_time = time()
        self.time_since_last_move = self.current_time - self.last_time

        #Tests time since last movement to ensure snake is moving based on constant time instead of variable framerate.
        if self.time_since_last_move > (self.frame_time * self.scale / self.speed):

            #Reset movement buffer to allow next input
            self.buffer = False

            #Reset timer to next frame
            self.last_time = self.current_time

            #Make calculations!
            self.move_snake()

            #Check all removed and added coordinates, write to screen and update
            for px in self.removed_pixel: #remove flagged pixels
                self.draw_pixel(px[0], px[1], "background")
                self.removed_pixel = []
            self.draw_pixel(self.food_x, self.food_y, "text") #draw food
            self.draw_pixel(self.coord_dict[len(self.coord_dict)-1][0], self.coord_dict[len(self.coord_dict)-1][1], "snake") #draw snake
            pygame.display.update()


class snake_bot():
    def __init__(self, px_size):
        self.snake_pixel_size = px_size
        self.tuple_to_dir= {
            (-1, 0): "left",
            (1, 0): "right",
            (0, -1): "up",
            (0, 1): "down"
        }
        self.turn_log = [1, -1] #-1 for left turn, +1 for right turn. Used when running into self.

    #Shrinks value down to a -1/0/1 value
    def unit_vec(self, length):
        outp = 0
        if length > 0:
            outp = 1
        elif length < 0:
            outp = -1
        return outp

    #Returns NSEW direction based on current direction and L/R choice
    def turn(self, input_dir, left_or_right):
        if left_or_right == "left":
            outp = (-input_dir[1], input_dir[0])
        elif left_or_right == "right":
            outp = (input_dir[1], -input_dir[0])
        return outp

    #Get current state of game and compute any necessary moves
    def get_move(self, game):
        #pull values from game
        snake = game.coord_dict
        snake_head = snake[len(snake)-1]
        food = (game.food_x, game.food_y)
        dir = game.direction

        #Calculate distances from snake to food. Gives buffer of scale
        x_diff = food[0] - snake_head[0]
        y_diff = food[1] - snake_head[1]
        for diff in [x_diff, y_diff]:
            if diff <= self.snake_pixel_size:
                diff = 0

        #check necessary directions to food, divide down to -1/0/1 value
        needed_dirs = (self.unit_vec(x_diff), self.unit_vec(y_diff))

        #if stopped (), start going up. The bot can then take it from there.
        if dir == (0,0):
            return "up"

        #If one of the directions matches up, do nothing
        if dir[0] == needed_dirs[0] or dir[1] == needed_dirs[1]:
            pass
        #Otherwise, check if left or right is better to turn
        else:
            #makes copy of directional tuple, rotates it and the necessary direction until in standard frame
            dir_cp = dir
            while dir_cp != (0, -1):
                dir_cp = self.turn(dir_cp, "left")
                needed_dirs = self.turn(needed_dirs, "left")

            #Once in proper frame, check +/- on the x-axis to see if we need to turn right or left
            if needed_dirs[0] > 0:
                return self.tuple_to_dir[self.turn(dir, "left")]
            elif needed_dirs[0] < 0:
                return self.tuple_to_dir[self.turn(dir, "right")]

def main():
    pygame.init()
    screen = pygame.display.set_mode((disp_width, disp_height))
    pygame.display.set_caption("Snake by Duncan")
    clock = pygame.time.Clock()

    snek = snake_game(screen, disp_width, disp_height, speed, fps, scale)
    bot = snake_bot(scale)

    while True:
        for event in pygame.event.get():
            #handles exiting on X
            if event.type == pygame.QUIT:
                pygame.quit()
            #handles manual direction switching
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snek.change_direction("up")
                if event.key == pygame.K_DOWN:
                    snek.change_direction("down")
                if event.key == pygame.K_LEFT:
                    snek.change_direction("left")
                if event.key == pygame.K_RIGHT:
                    snek.change_direction("right")

        if run_bot == True:
            snek.change_direction(bot.get_move(snek))

        snek.update_game()
        clock.tick(fps)


if __name__ == "__main__":
    main()