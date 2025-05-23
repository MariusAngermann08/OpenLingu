#Install all needed modules from requirements.txt via pip
import subprocess
import sys
import os

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

print("All needed modules installed")

