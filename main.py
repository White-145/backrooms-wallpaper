from PIL import Image
from random import random

from maze import Maze, N as UP, S as DN, W as LF, E as RG

### parameters

# result image will be saved as <filename>.png
filename = "wallpaper"
# your screen size (width, height)
screen_size = (1366, 768)
# background color
background = (77, 77, 77, 255)
# width, height of backrooms in tiles
size = (40, 40)
# percentage of tile being without walls
shatter_percentage = 0.5

# tile parameters
tile_size = 22
tile_size_outlineless = 20
tile_grid = (4, 4)

FRONT_WALL = (255, 0, 0, 255)
BACK_WALL  = (0, 0, 255, 255)
FLOOR      = (0, 255, 0, 255)
# should be different
OUTLINE_1  = (0, 0, 0, 255)
OUTLINE_2  = (255, 255, 255, 255)

# wall directions to tile id
tile_ids = {
	frozenset({UP, DN, LF, RG}): 0,
	frozenset({UP, DN, LF}): 1,
	frozenset({UP, DN, RG}): 2,
	frozenset({UP, LF, RG}): 3,
	frozenset({DN, LF, RG}): 4,
	frozenset({UP, DN}): 5,
	frozenset({UP, LF}): 6,
	frozenset({UP, RG}): 7,
	frozenset({DN, LF}): 8,
	frozenset({DN, RG}): 9,
	frozenset({LF, RG}): 10,
	frozenset({UP}): 11,
	frozenset({DN}): 12,
	frozenset({LF}): 13,
	frozenset({RG}): 14,
	frozenset({}): 15,
}

def grid(right, down, left=0, up=0):
	for y in range(down - up):
		for x in range(right - left):
			yield (x + left, y + up)

# get screen position
def pos(x, y):
	# screen pos = isometric pos + half screen - quarter largest isometric pos - half tile - 1
	# tile size in pos Y is halfed due to tile shape
	return (
		(x - y) * tile_size_outlineless // 2 + screen_size[0] // 2 - (size[0] - size[1]) * tile_size_outlineless // 4 - tile_size_outlineless // 2 - 1,
		(x + y) * tile_size_outlineless // 4 + screen_size[1] // 2 - (size[0] + size[1]) * tile_size_outlineless // 8 - tile_size_outlineless // 4 - 1
	)

def clamp(num, min, max):
	if num < min:
		return min
	if num > max:
		return max
	return num

# get tiles
tiles_image = Image.open("resources/tiles.png")
tiles = []
for x, y in grid(*tile_grid):
	tiles.append(tiles_image.crop((
		x * tile_size,
		y * tile_size,
		(x + 1) * tile_size,
		(y + 1) * tile_size
	)))

# gen

generation = Maze.generate(*map(lambda x: x + 2, size))

img = Image.new("RGBA", screen_size, background)

for x, y in grid(*size):
	if x == 0 and y == 0:
		img.paste(t := tiles[tile_ids[frozenset({UP, LF})]], pos(x, y), t)   # corner
	elif y == 0:
		img.paste(t := tiles[tile_ids[frozenset({UP})]], pos(x, y), t)  # right wall
	elif x == 0:
		img.paste(t := tiles[tile_ids[frozenset({LF})]], pos(x, y), t)  # left wall
	else:
		img.paste(t := tiles[tile_ids[frozenset({})]], pos(x, y), t)  # floor

	if random() > shatter_percentage:
		cell = generation[x, y]
		img.paste(t := tiles[tile_ids[frozenset(cell.walls)]], pos(x, y), t)

# clean image

left_up =    (clamp(pos(0, size[1] - 1)[0], 0, screen_size[0]), clamp(pos(0, 0)[1], 0, screen_size[1]))
right_down = (clamp(pos(size[0] - 1, 0)[0] + tile_size, 0, screen_size[0]), clamp(pos(size[0] - 1, size[1])[1] + tile_size, 0, screen_size[1]))

# add outlines
for x, y in grid(*right_down, *left_up):
	try:
		current = img.getpixel((x, y))
		up = img.getpixel((x, y - 1))
		if current in (background, FLOOR) and up not in (FRONT_WALL, BACK_WALL):
			right = img.getpixel((x + 1, y))
			left = img.getpixel((x - 1, y))
			if right in (FRONT_WALL, BACK_WALL) or left in (FRONT_WALL, BACK_WALL):
				img.putpixel((x, y), OUTLINE_1)

		if current == background and up not in (background, OUTLINE_2):
			img.putpixel((x, y), OUTLINE_2)
	except IndexError:
		# i was to lazy to make checks...
		pass

# replace colors with textures
texture_front_wall = Image.open("resources/texture_front_wall.png")
texture_back_wall = Image.open("resources/texture_back_wall.png")
texture_floor = Image.open("resources/texture_floor.png")
texture_outline = Image.open("resources/texture_outline.png")

for x, y in grid(*right_down, *left_up):
	current = img.getpixel((x, y))
	if current == FRONT_WALL:
		img.putpixel((x, y), texture_front_wall.getpixel((x % texture_front_wall.size[0], y % texture_front_wall.size[1])))
	elif current == BACK_WALL:
		img.putpixel((x, y), texture_back_wall.getpixel((x % texture_back_wall.size[0], y % texture_back_wall.size[1])))
	elif current == FLOOR:
		img.putpixel((x, y), texture_floor.getpixel((x % texture_floor.size[0], y % texture_floor.size[1])))
	elif current in (OUTLINE_1, OUTLINE_2):
		img.putpixel((x, y), texture_outline.getpixel((x % texture_outline.size[0], y % texture_outline.size[1])))

img.save(f'{filename}.png')