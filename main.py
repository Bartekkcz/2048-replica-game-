import pygame
import random
import math

pygame.init()
#Frames Per Second
FPS = 60    
#Frame size
WIDTH, HEIGHT = 800, 800                    
ROWS = 4
COLS = 4
#Height of one rectangle, Width of one rectangle
RECT_HEIGHT = HEIGHT // ROWS                
RECT_WIDTH = WIDTH // COLS                  

OUTLINE_COLOR = (187, 173, 160)             #RGV Gray
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)          #RGV Light Gray
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20                               #Speed of tiles movement

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")          #Title of the window


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 218),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 155),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, column):
        self.value = value
        self.row = row
        self.column = column
        self.x = column * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        #Put a surface on the screen
        window.blit(                    
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2)
            ), 
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.column = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.column = math.floor(self.x / RECT_WIDTH)
    
    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

def draw_grid(window):
    for row in range(1, ROWS):                  #We can skip the first row (already drawn)
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    
    for column in range(1, COLS):               #We can skip the first row (already drawn)
        x = column * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(WINDOW)

    pygame.display.update()

def get_random_position(tiles):
    row = None
    column = None
    while True:
        row = random.randrange(0, ROWS)
        column = random.randrange(0, COLS)
        #Check with dictionary if a tile already exist in generated position
        if f"{row}{column}" not in tiles:
            break

    return row, column

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        #sort the tiles, which one moves first
        sort_func = lambda x: x.column
        reverse = False
        #how much move each tile in each frame
        #-MOVE_VEL - moves to the left
        delta = (-MOVE_VEL, 0)  

        boundary_check = lambda tile: tile.column == 0
        #if there isnt a tile -> return nothing
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.column - 1}")
        #check if we move completly inside the other tile 
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        #stop moving if we reach the border of the other tile
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
            )
        ceil = True

    elif direction == "right":
        #sort the tiles, which one moves first
        sort_func = lambda x: x.column
        reverse = True
        #how much move each tile in each frame
        #MOVE_VEL - moves to the right
        delta = (MOVE_VEL, 0)  
        #right boundary
        boundary_check = lambda tile: tile.column == COLS - 1
        #if there isnt a tile -> return nothing
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.column + 1}")
        #check if we move completly inside the other tile 
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        #stop moving if we reach the border of the other tile
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x 
            )
        ceil = False

    elif direction == "up":
        #sort the tiles, which one moves first
        sort_func = lambda x: x.row
        reverse = False
        #how much move each tile in each frame
        #-MOVE_VEL - moves up
        delta = (0, -MOVE_VEL)  

        boundary_check = lambda tile: tile.row == 0
        #if there isnt a tile -> return nothing
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.column}")
        #check if we move completly inside the other tile 
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        #stop moving if we reach the border of the other tile
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_WIDTH + MOVE_VEL
            )
        ceil = True

    elif direction == "down":
        #sort the tiles, which one moves first
        sort_func = lambda x: x.row
        reverse = True
        #how much move each tile in each frame
        #MOVE_VEL - moves down
        delta = (0, MOVE_VEL)  

        boundary_check = lambda tile: tile.row == ROWS - 1
        #if there isnt a tile -> return nothing
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.column}")
        #check if we move completly inside the other tile 
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        #stop moving if we reach the border of the other tile
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
            )
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            #move to the border
            if not next_tile:
                tile.move(delta)
            #move and merge
            elif (
                tile.value == next_tile.value 
                and tile not in blocks 
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    #remove merged tile
                    sorted_tiles.pop(i)
                    #ensure we dont do double merge
                    blocks.add(next_tile)
            #move to the next tile
            elif move_check(tile, next_tile):
                tile.move(delta)
            #no place for movement
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)
    
    return end_move(tiles)

def end_move(tiles):
    if len(tiles) == 16:
        return "lost"
    
    row, column = get_random_position(tiles)
    tiles[f"{row}{column}"] = Tile(random.choice([2, 4]), row, column)
    return "continue"

def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.column}"] = tile

    draw(window, tiles)

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, column = get_random_position(tiles)
        tiles[f"{row}{column}"] = Tile(2, row, column)

    return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True

    #Dictionary
    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   #Quit the game
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, "left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")
        draw(WINDOW, tiles)
        
    pygame.quit()

if __name__ == "__main__":
    main(WINDOW)