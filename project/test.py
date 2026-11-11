from __future__ import annotations
import os
import shutil
import sys
import time
from collections import deque
from pathlib import Path
import builtins
width, height = 80, 24

import time

width = 80

def storyframe(title, lines, prompt):
    border = "+" + "-" * 62 + "+"

    print()
    print(border.center(width - 1))
    print(("|" + title.center(62) + "|").center(width - 1))
    print(border.center(width - 1))

    for line in lines:
        print(
            ("|" + line.center(62) + "|").center(width - 1),
            flush=True
        )

        if line:
            time.sleep(0.5)

    print(border.center(width - 1))
    print(prompt.center(width - 1), flush=True)


storyframe(
    "Floor 1",
    [
        "You wake up in a dark room.",
        "There is a locked door in front of you.",
        "You hear footsteps outside..."
    ],
    "Press ENTER to continue"
)
