from __future__ import annotations
import os
import shutil
import sys
import time
from collections import deque
from pathlib import Path

width, height = 80, 24
mapdir = Path(__file__).resolve().parent / "maps"
Titlepagedir = Path(__file__).resolve().parent / "Titlepage" / "titlepage.txt"

puz = [
    ("""To advance to the next floor, you must choose ONE correct choice\n 
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
    (),
    (),
    (),
]
floors = ()

def titlepage():
    clear()
    print(Titlepagedir.read_text(encoding="utf-8"))
    print("Press any key to start, or Q to quit.")
    while True:
        action = readkey("")
        if action == "q":
            sys.exit()
        else:
            break

def floorloading(floor):
    path = mapdir / f"floor_{floor + 1}.txt"
    rows = tuple(path.read_text(encoding="utf-8").splitlines())
    if not rows or not 3 <= len(rows) <= 17:
        raise ValueError(f"{path.name}: map height must be 3 to 17 rows")
    width = len(rows[0])  
    return rows


def readkey(prompt):
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


def clear():
    sys.stdout.write("\033[2J\033[H")


def termsizecheck():
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


def tilecheck(rows, tile):
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == tile:
                return x, y
    raise ValueError(f"Missing tile: {tile}")


def navigation(rows, start, goal):
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


def render(room, floor, player, guard, solved, message):
    rows = [list(row) for row in room]
    px, py = player
    gx, gy = guard
    rows[gy][gx] = "G"
    rows[py][px] = "@"

    clear()
    print(f"FIVE FLOORS BELOW                         FLOOR {floor + 1}/3")
    print("# = wall   @ = player   G = guard   P = puzzle   E = exit")   
    for y, row in enumerate(rows):
        seerow = []
        for x, char in enumerate(row):
            if abs(x - px) <= 2 and abs(y - py) <= 2:
                seerow.append(char)
            else:
                seerow.append("■")
                
        print("".join(seerow))
    print(message)

def answerchoose(floor) -> bool:
    clue, opt, ans = puz[floor]
    clear()
    print(f"FLOOR {floor + 1} PANEL")
    print(clue)
    print()
    for number, option in enumerate(opt, 1):
        print(f"{number}. {option}")
    if floor == 2:
        print("are you ready to pull the lever and exit?", end="", flush=True)
    else:
        print("Choose 1, 2, 3, 4 or 5: ", end="", flush=True)
    return readkey("") == ans


def main():
    floor = 0
    solved: set[int] = set()
    message = "Your goal is to reach the panel and try to solve it, then use the lift and escape!"
    mov = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}
    titlepage()
    while True:
        if termsizecheck() == True:
            continue
        room = floorloading(floor)
        player = tilecheck(room, "@")
        guard = tilecheck(room, "G")

        while True:
            render(room, floor, player, guard, solved, message)
            act = readkey("")
            if act == "q":
                print("\nThanks for playing.")
                return
            if act in mov:
                dx, dy = mov[act]
                goplace = player[0] + dx, player[1] + dy
                if room[goplace[1]][goplace[0]] == "#":
                    message = "A wall blocks the way. Try another direction."
                    continue
                player = goplace
                guard = navigation(room, guard, player)
                if guard == player:
                    floor, solved = floor, set()
                    message = "The guard caught you. You are sent back to the starting point, all panels reset."
                    break
                message = "The guard moves closer..." if guard != tilecheck(room, "G") else "Keep moving."
                continue
            if act == "e":
                if player == tilecheck(room, "P"):
                    if floor in solved:
                        message = "This panel is already solved. Go to E."
                        continue
                    if answerchoose(floor):
                        solved.add(floor)
                        message = "Correct. The lift unlocks; the next floor's panel is linked to this one."
                    else:
                        message = "Answer wrong"
                        guard = navigation(room, guard, player)
                        if guard == player:
                            floor, solved = floor, set()
                            message = "You are caught at the panel. Back to the starting point, all panels reset."
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

if __name__ == "__main__":
    main()