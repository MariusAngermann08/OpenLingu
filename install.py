#Install all needed modules from requirements.txt via pip
import subprocess
import sys


#Install all needed modules from requirements.txt via pip
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

print("All needed modules installed")

print("Installation finished")

#Wait for user to press enter
input("Press Enter to exit...")