#!/usr/bin/python3

import subprocess
import os.path

cwd = os.path.dirname(os.path.abspath(__file__))

if os.path.islink(__file__):
    cwd = os.path.dirname(os.path.abspath(os.readlink(__file__)))

p1 = subprocess.Popen(['python3', './main.py'], cwd=cwd)

try:
    input()
except:
    pass

try:
    p1.kill()
except:
    pass

exit(0)
