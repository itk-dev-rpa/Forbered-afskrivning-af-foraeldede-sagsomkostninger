"""The main file of the robot which will install all requirements in
a virtual environment and then start the actual process.
"""

import subprocess
import os
import sys

script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

subprocess.run("python -m venv .venv", check=True)
subprocess.run(r'.venv\Scripts\pip install .', check=True)

command_args = [r".venv\Scripts\python", "-m", "forbered_afskrivining_af_foraeldede_sagsomkostninger"] + sys.argv[1:]

subprocess.run(command_args, check=True)
