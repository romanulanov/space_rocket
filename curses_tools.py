LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


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


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def check_boundary(canvas,
                   row,
                   column,
                   text,
                   ):
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
