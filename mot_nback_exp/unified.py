from nback import main as nback_main
from MOT_exp_main import main as MOT_main
from messagescreens import *
import pygame as pg

def main():
    pg.init()
    while True:
        gametype = user_info("Gametype ('MOT' or 'NBACK'): ")
        if gametype == 'MOT' or gametype == 'mot':
            mot_screen()
            MOT_main()
        elif gametype.lower() == 'nback' or gametype.lower() == 'n-back':
            nback_screen()
            nback_main()

if __name__ == "__main__":
    main()