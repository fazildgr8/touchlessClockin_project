from subprocess import *
import time

def main():
    Popen('python main.py')
    time.sleep(3)
    Popen('python player.py')

if __name__ == "__main__":
    main()

