import time
import asyncio
import curses
import random
from itertools import cycle


LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
TIC_TIMEOUT = 0.005
spaceship_row = 0
spaceship_column = 0
stars = [
    '+',
    '*',
    '.',
    ':',
]


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()
        if pressed_key_code == -1:
            break
    
        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1
    
        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1
    
        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1
    
        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1
    
    
    return rows_direction, columns_direction, space_pressed


def check_boundary(canvas,
                   row,
                   column,
                   text,):
  rows, columns = get_frame_size(text)
  max_y, max_x = canvas.getmaxyx()
  if row < 0:
      row = 0
  elif row + rows > max_y:
      row = max_y - rows
  if column < 0:
      column = 0
  elif column + columns > max_x:
      column = max_x - columns
  return row, column


def draw_frame(canvas,
               start_row,
               start_column,
               text,
               negative=False,
               ):
  rows_number, columns_number = canvas.getmaxyx()

  for row, line in enumerate(text.splitlines(), round(start_row)):
    if row < 0:
      continue

    if row >= rows_number:
      break

    for column, symbol in enumerate(line, round(start_column)):
      if column < 0:
        continue

      if column >= columns_number:
        break

      if symbol == ' ':
        continue

      if row == rows_number - 1 and column == columns_number - 1:
        continue

      symbol = symbol if not negative else ' '
      canvas.addch(row, column, symbol)


async def animate_spaceship(canvas):
  global spaceship_row, spaceship_column
  rocket_frames = []
  for i in range(1, 3):
    with open(f"images/rocket_frame_{i}.txt", "r") as my_file:
      rocket_frames.append(my_file.read())
  iterator = cycle(rocket_frames)
  while True:
    global rocket_frame
    rocket_frame = next(iterator)
    
    draw_frame(canvas, spaceship_row, spaceship_column, rocket_frame)
    canvas.refresh()
    
    await asyncio.sleep(0)
    draw_frame(canvas, spaceship_row, spaceship_column, rocket_frame, negative=True)
    

async def fire(canvas,
               start_row,
               start_column,
               rows_speed=-0.3,
               columns_speed=0):

  row, column = start_row, start_column

  canvas.addstr(round(row), round(column), '*')
  await asyncio.sleep(0)

  canvas.addstr(round(row), round(column), 'O')
  await asyncio.sleep(0)
  canvas.addstr(round(row), round(column), ' ')

  row += rows_speed
  column += columns_speed

  symbol = '-' if columns_speed else '|'

  rows, columns = canvas.getmaxyx()
  max_row, max_column = rows - 1, columns - 1

  curses.beep()

  while 0 < row < max_row and 0 < column < max_column:
    canvas.addstr(round(row), round(column), symbol)
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')
    row += rows_speed
    column += columns_speed


async def blink(canvas, row, column, symbol):
  while True:
    canvas.addstr(row, column, symbol, curses.A_DIM)
    for _ in range(30):
      await asyncio.sleep(0)

    canvas.addstr(row, column, symbol)
    for _ in range(0):
      await asyncio.sleep(0)

    canvas.addstr(row, column, symbol, curses.A_BOLD)
    for _ in range(30):
      await asyncio.sleep(0)

    canvas.addstr(row, column, symbol)
    for _ in range(30):
      await asyncio.sleep(0)

    for _ in range(random.randint(1, 30)):
      await asyncio.sleep(0)


def draw(canvas):
  curses.curs_set(0)
  canvas.border()
  global spaceship_row, spaceship_column
  canvas.nodelay(True)
  max_y, max_x = canvas.getmaxyx()
  coroutines_fire = [
      fire(canvas, start_row=max_y - 1, start_column=max_x // 2)
  ]
  
  while True:
    
    for coroutine in coroutines_fire.copy():
      try:
        coroutine.send(None)
      except StopIteration:
        coroutines_fire.remove(coroutine)
    if len(coroutines_fire) == 0:
      break
    
    time.sleep(TIC_TIMEOUT)
  coroutines = []
  
  coroutines.append(animate_spaceship(canvas))
  for i in range(1000):
    coroutines.append(
        blink(canvas,
              random.randint(1, max_y - 2),
              random.randint(1, max_x - 2),
              random.choice(stars)
             )
             )

  while True:
    for coroutine in coroutines:
        try:
            coroutine.send(None)
            canvas.refresh()
        except StopIteration:
            break

    global rocket_frame
    rows_direction, columns_direction, space_pressed = read_controls(canvas)
    draw_frame(canvas, spaceship_row, spaceship_column, rocket_frame, negative=True)
    canvas.border()
    spaceship_row += rows_direction
    spaceship_column += columns_direction
    spaceship_row, spaceship_column = check_boundary(canvas, spaceship_row, spaceship_column, rocket_frame)
    time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
