import asyncio
import curses
import random

from curses_tools import read_controls, check_boundary, draw_frame

from itertools import cycle
from time import sleep

TIC_TIMEOUT = 0.005

spaceship_row = 0
spaceship_column = 0
stars = [
    '+',
    '*',
    '.',
    ':',
]


async def animate_spaceship(canvas):
    spaceship_row = 0
    spaceship_column = 0
    rocket_frames = []
    for i in range(1, 3):
        with open(f"images/rocket_frame_{i}.txt", "r") as my_file:
            rocket_frames.append(my_file.read())
           

    iterator = cycle(rocket_frames)
   
    while True:
        rocket_frame = next(iterator)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        spaceship_row += rows_direction
        spaceship_column += columns_direction
        spaceship_row, spaceship_column = check_boundary(canvas,
                                                            spaceship_row,
                                                            spaceship_column,
                                                            rocket_frame)
        for _ in range(2):
            draw_frame(canvas,
                    spaceship_row,
                    spaceship_column,
                    rocket_frame,
                    
                    )
            await asyncio.sleep(0)
            draw_frame(canvas,
                    spaceship_row,
                    spaceship_column,
                    rocket_frame,
                    negative=True,
                    )
            
            
            await asyncio.sleep(0)
        


async def fire(canvas,
               start_row,
               start_column,
               rows_speed=-0.3,
               columns_speed=0,
               ):

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
    canvas.nodelay(True)
    
    max_y, max_x = canvas.getmaxyx()
    coroutines = [fire(canvas, start_row=max_y - 1, start_column=max_x // 2)]

    coroutines.append(animate_spaceship(canvas))
    for i in range(1000):
        coroutines.append(
            blink(canvas,
                  random.randint(0, max_y - 1),
                  random.randint(0, max_x - 1),
                  random.choice(stars)
                  )
                )

    while True:
        canvas.refresh()
        canvas.border()
        for coroutine in coroutines[:]:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)       
        sleep(TIC_TIMEOUT) 
        

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
