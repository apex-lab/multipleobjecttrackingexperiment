from nback import main as nback_main
from MOT_exp_main import main as MOT_main
from messagescreens import *
import pygame as pg

def main():
    play_again = True
    pg.init()
    while play_again == True:
        gametype = user_info("Gametype ('MOT' or 'NBACK'): ")
        if gametype.lower() == 'mot':
            mot_screen()
            play_again = MOT_main(True)
        if gametype.lower() == 'nback':
            nback_screen()
            play_again = nback_main(True)

if __name__ == "__main__":
    main()