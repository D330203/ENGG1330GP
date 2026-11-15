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
picpuzdir = Path(__file__).resolve().parent / "picturepuz"
loadingdir = Path(__file__).resolve().parent / "loadingscreen" / "loading1.txt"

puz = [
    ("""THE FOUR VOICES

Four voices speak through the building's loudspeaker.
A warning is taped to the control panel:

"Exactly ONE statement is true.
There is only ONE safe circuit."
    
Voice 1: The safe circuit is A or B.
Voice 2: The safe circuit is C or D.
Voice 3: The safe circuit is NOT C.
Voice 4: The safe circuit is E.

Which circuit should you activate?""", ("Circuit A", "Circuit B", "Circuit C", "Circuit D", "Circuit E"), "3"),

    ("""THE ONE-WAY ESCALATOR

A note reads: "To go down, first go up."

This is a model shown on the panel, not the maze.
Start on 3F. Reach the exit on 0F.
U: Take the escalator UP one floor.
D: Take the stairs DOWN two floors.
D is available ONLY FROM an EVEN floor.
Only 0F to 4F exist. Never leave this range.
The route ends when you reach 0F.

Which route reaches the exit?""", ("U - U - D", "D - U - D", "U - D - D", "U - D - U","U - U - U"), "3"),
    (("""THE MOONLIT FOUNTAIN

Read the digits from the SHORTEST column to the TALLEST.
Each ■ represents one unit of height.

         ■
         ■
         ■       ■
 ■       ■       ■
 ■       ■       ■
LEFT   MIDDLE  RIGHT
 7       2       4

What is the three-digit code?"""),("724", "247", "427", "742","274"), "4")
]
floors = ()

openingstory = [("23:59. You stayed late at HKU to finish a project."),
                ("Inside the Chong Yuet Ming Building, the lift stops."),
                ("Its doors open onto an unfamiliar corridor."),
                (""),
                ("Your phone has no signal. Yet a message arrives:"),
                ("[UNKNOWN NUMBER]"),
                ("'Do not follow the person in uniform.'"),
                ("'Solve the puzzles on three floors, Unlock the courtyard door. I can help you escape.'"),
                (""),
                ("Footsteps echo behind you."),
                ("A figure stands at the end of the corridor."),
                ("The lights go out."),
                ("Only your phone screen remains.")

]
endingstory = [("You push the courtyard door open."),
                (""),
                ("""Cold night air touches your face.
The campus looks familiar again."""),
                ("Your phone reconnects."),
                (""),
                ("Behind you, the door clicks out"),
                ("YOU ESCAPED"),
]
endingstory2 = [
                ("Your phone vibrates."),
                ("[UNKNOWN NUMBER]"),
                ("'Thank you.'"),
                ("'I finally got out, too.'"),
                ("You turn around."),
                (""),
                ("There is nobody here"),
                ("GAME COMPLETED"),

]

def blackscreen(s):
    print("\033[48;2;0;0;0m\033[?25l", end="")
    clear()
    sys.stdout.flush()
    try:
        time.sleep(s)
    finally:
        print("\033[0m\033[?25h", end="", flush=True)

def storyteling():
    for line in openingstory:
        if termsizecheck() == True:
            clear()
        else:
            print(line)
            time.sleep(1.0)
    print("\nPress any key to continue, or Q to quit.")
    action = readkeyboard("")
    if action == "q":
        sys.exit() 
    else:
        pass

def showloadingscreen():
    with open(loadingdir, "r") as f:
        loading_lines = f.readlines()
    for line in loading_lines:
        if termsizecheck() == True:
            clear()
        else:
            print(line, end="")
            time.sleep(0.08)

def ending():
    for line in endingstory:
        if termsizecheck() == True:
            clear()
        else:
            print(line)
            time.sleep(1.0)
    blackscreen(3.0)
    for line in endingstory2:
        if termsizecheck() == True:
            clear()
        else:
            print(line)
            time.sleep(1.0)
    print("\nPress R to restart, or Q to quit.")
    action = readkeyboard("")
    if action == "q":
        sys.exit() 
    else:
        pass

def titlepage():
    clear()
    print(Titlepagedir.read_text(encoding="utf-8"))
    print("Press any key to start, or Q to quit.")
    while True:
        action = readkeyboard("")
        if action == "q":
            sys.exit()
        else:
            break

def floorloading(floor):
    path = mapdir / f"floor_{floor + 1}.txt"
    rows = tuple(path.read_text(encoding="utf-8").splitlines())
    width = len(rows[0])  
    return rows


def readkeyboard(prompt):
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
    print(f"THREE FLOORS IN TOTAL | FLOOR {floor + 1}/3 | Press E to interact with P or E")
    print("# = wall   @ = player   G = guard   P = puzzle   E = exit")   
    #print("# = wall   @ = player   G = guard   P = puzzle   U = next floor  D = previous floor  E = exit")
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
    print("Choose 1, 2, 3, 4 or 5: ", end="", flush=True)
    return readkeyboard("") == ans


def main():
    
    floor = 0
    solved = set()
    message = "Your goal is to reach the panel and try to solve it, use the lift and escape!"
    mov = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}
    titlepage()
    clear()
    storyteling()
    blackscreen(1.0)
    showloadingscreen()

    while True:
        if termsizecheck() == True:
            continue
        room = floorloading(floor)
        player = tilecheck(room, "@")
        guard = tilecheck(room, "G")

        while True:
            render(room, floor, player, guard, solved, message)
            act = readkeyboard("")
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
                        ending()
                        
                        print("Press R to restart, or Q to quit.")
                        while True:
                            again = readkeyboard("")
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