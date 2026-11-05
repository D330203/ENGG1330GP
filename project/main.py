from __future__ import annotations

import os
import shutil
import sys
import time
from collections import deque
from pathlib import Path

width, height = 80, 24
mapdirectory = Path(__file__).resolve().parent / "maps"
Titlepagedir = Path(__file__).resolve().parent / "Titlepage" / "titlepage.txt"

puz = [
    ("""To advance to the next floor, you must choose ONE correct door\n 
    RULE: Among the three dead wraiths, exactly TWO sentences are TRUE, ONE sentence is FALSE.\n
    Wraith 1: The correct door either A, B or E.\n
    Wraith 2: The correct door is not B.\n
    Wraith 3: The correct door is either B or C.\n
    Use logic deduction to find the correct door. Choose wisely!"""
     , ("A", "B", "C", "D", "E"), "2"),
    ("""You stand before a 4-digit combination lock.\n
    There are four notes left behind by a previous prisoner to help you crack it.\n
    Clue 1: 0 2 5 9 | One digit is correct and in the correct position.\n
    Clue 2: 5 1 9 3 | Two digits are correct, one of them is in the correct position.\n
    Clue 3: 9 4 1 6 | Two digits are correct, one of them is in the correct position.\n
    Clue 4: 4 8 2 7 | None of these digits are in the secret code.\n
    Work out the 4-digit secret code!"""
     , ("5394", "5193", "5160", "0294", "5196"), "3"),
    ("A lever that controls the gate of exit appears in front of you ", ("yes", "no"), "1"),
    ("A lock asks: how many sides has a hexagon?", ("5", "6", "8"), "2"),
    ("The exit asks: what is 5 squared?", ("10", "20", "25"), "3"),
]
floors = ("Lobby", "Records", "Laboratory", "Control", "Roof access")

def titlepage() -> None:
    clear()
    print(Titlepagedir.read_text(encoding="utf-8"))
    print("Press any key to start, or Q to quit.")
    while True:
        action = readkey("")
        if action == "q":
            sys.exit()
        else:
            break

def floorloading(floor: int) -> tuple[str, ...]:
    path = mapdirectory / f"floor_{floor + 1}.txt"
    rows = tuple(path.read_text(encoding="utf-8").splitlines())
    if not rows or not 3 <= len(rows) <= 17:
        raise ValueError(f"{path.name}: map height must be 3 to 17 rows")
    width = len(rows[0])
    """
    if not 3 <= width <= 78 or any(len(row) != width for row in rows):
        raise ValueError(f"{path.name}: rows must have the same width (3 to 78)")
    if any(char not in "# @GPE" for row in rows for char in row):
        raise ValueError(f"{path.name}: unsupported map character")
    for marker in "@GPE":
        if sum(row.count(marker) for row in rows) != 1:
            raise ValueError(f"{path.name}: expected exactly one {marker}")
    if any(char != "#" for char in rows[0] + rows[-1]):
        raise ValueError(f"{path.name}: top and bottom edges must be walls")
    if any(row[0] != "#" or row[-1] != "#" for row in rows):
        raise ValueError(f"{path.name}: left and right edges must be walls")
    """    
    return rows


def readkey(prompt: str) -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    if os.name == "nt":
        import msvcrt
        key = msvcrt.getwch()
        return key.lower()

    import termios
    import tty

    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1).lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def clear() -> None:
    sys.stdout.write("\033[2J\033[H")


def termsizecheck() -> bool:
    size = shutil.get_terminal_size((width, height))
    if size.columns >= width and size.lines >= height:
        return False
    clear()
    message = ["Five Floors Below", "", "Please resize the terminal to at least", "80 columns by 24 rows."]
    visible = message[: max(1, size.lines)]
    for index, line in enumerate(visible):
        sys.stdout.write(line[: max(1, size.columns)])
        if index < len(visible) - 1:
            sys.stdout.write("\n")
    sys.stdout.flush()
    time.sleep(1.0)
    return True


def tilecheck(rows: tuple[str, ...], tile: str) -> tuple[int, int]:
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == tile:
                return x, y
    raise ValueError(f"Missing tile: {tile}")


def navigation(rows: tuple[str, ...], start: tuple[int, int], goal: tuple[int, int]) -> tuple[int, int]:
    queue = deque([(start, None)])
    visited = {start}
    directions = ((0, -1), (1, 0), (0, 1), (-1, 0))
    while queue:
        point, first_step = queue.popleft()
        if point == goal:
            return first_step or start
        for dx, dy in directions:
            nxt = point[0] + dx, point[1] + dy
            x, y = nxt
            if nxt in visited or rows[y][x] == "#":
                continue
            visited.add(nxt)
            queue.append((nxt, nxt if first_step is None else first_step))
    return start


def render(room: tuple[str, ...], floor: int, player: tuple[int, int], guard: tuple[int, int], solved: set[int], message: str) -> None:
    rows = [list(row) for row in room]
    px, py = player
    gx, gy = guard
    rows[gy][gx] = "G"
    rows[py][px] = "@"

    clear()
    print(f"FIVE FLOORS BELOW                         FLOOR {floor + 1}/3")
    print("# = wall   @ = you   G = patrol   P = puzzle   E = exit")   
    for y, row in enumerate(rows):
        visible_row = []
        for x, char in enumerate(row):
            if abs(x - px) <= 2 and abs(y - py) <= 2:
                visible_row.append(char)
            else:
                visible_row.append("■")
                
        print("".join(visible_row))
    print(message)

def answerchoose(floor: int) -> bool:
    clue, options, answer = puz[floor]
    clear()
    print(f"FLOOR {floor + 1} PANEL")
    print(clue)
    print()
    for number, option in enumerate(options, 1):
        print(f"{number}. {option}")
    if floor == 2:
        print("are you ready to pull the lever and exit?", end="", flush=True)
    else:
        print("Choose 1, 2, 3, 4 or 5: ", end="", flush=True)
    return readkey("") == answer


def play() -> None:
    floor = 0
    solved: set[int] = set()
    message = "Reach the panel, solve it, then use the lift. Make it to the roof!"
    moves = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}
    titlepage()
    while True:
        if termsizecheck():
            continue
        room = floorloading(floor)
        player = tilecheck(room, "@")
        guard = tilecheck(room, "G")

        while True:
            render(room, floor, player, guard, solved, message)
            action = readkey("")
            if action == "q":
                print("\nThanks for playing.")
                return
            if action in moves:
                dx, dy = moves[action]
                target = player[0] + dx, player[1] + dy
                if room[target[1]][target[0]] == "#":
                    message = "A wall blocks the way. That did not use a turn."
                    continue
                player = target
                guard = navigation(room, guard, player)
                if guard == player:
                    floor, solved = floor, set()
                    message = "The guard caught you. You are sent back to the starting point; all panels reset."
                    break
                message = "The guard moves closer..." if guard != tilecheck(room, "G") else "Keep moving."
                continue
            if action == "e":
                if player == tilecheck(room, "P"):
                    if floor in solved:
                        message = "This panel is already solved. Go to E."
                        continue
                    if answerchoose(floor):
                        solved.add(floor)
                        message = "Correct. The lift unlocks; the next floor's panel is linked to this one."
                    else:
                        message = "Wrong answer. The guard gets a turn."
                        guard = navigation(room, guard, player)
                        if guard == player:
                            floor, solved = floor, set()
                            message = "Caught at the panel. Back to the starting point; all panels reset."
                            break
                    continue
                if player == tilecheck(room, "E"):
                    if floor not in solved:
                        message = "The lift is locked. Solve this floor's panel first."
                    elif floor == 2:
                        clear()
                        print("YOU ESCAPED!")
                        print("You solved all five connected panels and reached the roof.")
                        print("Press R to restart, or Q to quit.")
                        while True:
                            again = readkey("")
                            if again == "r":
                                floor, solved = floor, set()
                                message = "A new run begins in the lobby."
                                break
                            if again == "q":
                                return
                        break
                    else:
                        floor += 1
                        message = f"Lift to floor {floor + 1}. Find the next panel."
                        break
                else:
                    message = "Nothing to use here. Move to P or E."
                continue
            message = "Use W, A, S, D to move; E to interact; Q to quit."


def main() -> None:
    try:
        play()
    except (OSError, ValueError) as exc:
        clear()
        print(f"Map error: {str(exc)[:68]}")
        print("Check that maps/floor_1.txt through floor_5.txt are included.")
    except KeyboardInterrupt:
        print("\nGame stopped.")

if __name__ == "__main__":
    main()