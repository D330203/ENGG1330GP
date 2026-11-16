Run command in Project_docker terminal: python3 project/main.py
ENGG1330 Subclass L, group 9
Container version: engg1330-project:2026-v03
Game name: CYM Escaper

demo link: https://drive.google.com/file/d/1lFZerLdVJLOry6AxtZ5UeRvEcE7BYWRF/view?usp=drivesdk

trailer link: https://canva.link/iuuepkf75jcsypt


Game purpose: the player "@" needs to pass through 3 levels of maze with avoiding the guard represented by notation "G", for each level of the maze, the player needs to find and reach the control panel "P", solve the puzzle before they reach the exit "E" and enters the next floor. The game ends when player reaches th exit of the third floor.

Rules: Use WASD for moving up, left, down and right respectively. Press E to interact with control panel "P" or exit "E". the guard is represented by "G". 

test & limitations: (Solved already): when the guard and the player enters the control panel or the exit at the same time, the program will clash, the command shows the player has already enters the next floor while on the displayed map, the player is still in the previous floor. 
A new "if" detection is added to deal with the condition above: as for the control panel: the player will be sent back to starting point, for exit, play can go to the next floor.

Contributions:
CHENG_JINGXING: Programming/ map designing
LI_KEXIN: Trailer video/ Story writing / Puzzle designing
MA_HEII: Gameplay designing / Demo video


