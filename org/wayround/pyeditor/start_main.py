#!/usr/bin/python3

import subprocess


p1 = subprocess.Popen(['python3', './main.py'])

try:
    input()
except:
    pass

try:
    p1.kill()
except:
    pass

exit(0)
