#! /usr/bin/python3

import pyfiglet
from termcolor import colored
import random
import os

#FONT SELECTION
fonts = ["big","bubble","pagga","script","shadow","slant","small","smblock"]

#COLOR SELECTION
colors = ["grey","red","green","yellow","blue","magenta","cyan","white"]

ran_font = random.choice(fonts)
ran_color = random.choice(colors)
banner = pyfiglet.figlet_format("    PASS GUARD",font = ran_font)
ascii_art = ('''
	              _______________
	              \      _      /         __
	               \_____()____/         /  )
	                ===========         /  /
	               (# O\| |/O #)       /  /
	                \   (_)   /       /  /
	                |\ '---' /|      /  /
	        _______/  \_____/  \____/ o_|
	       /       \  /     \  /   / o_|
	      / |           o|        / o_| \\
	     /  |  _____     |       / /   \ \\
	    /   |  |===|    o|      / /\    \ \\
	   |    |   \_/      |     / /  \    \ \\
	   |    |___________o|__/----)   \    \ \\
	   |    '              ||  --)    \     |
	   |___________________||  --)     \    /
	        |           o|          |   \__/
	        |            |          |
''')
def bann():
	os.system("clear")
	print (colored(ascii_art + "\n\n" + banner , ran_color))
