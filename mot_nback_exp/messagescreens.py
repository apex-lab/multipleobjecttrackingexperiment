import pygame as pg
import os
from MOT_constants import *
import sys

# == Set window ==
x, y = 50, 50
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
win = pg.display.set_mode((0,0), pg.FULLSCREEN)
pg.display.set_caption(title)

# == Define colors. ==
background_col = GREY
hover_col = DARKSLATEGREY
click_col = GREENYELLOW
select_col = YELLOW


def wait_key():
    """function to wait key press"""
    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == pg.K_f:
                return


def draw_square(display=win):
        # -- Function to draw circle onto display
        pg.draw.rect(display, WHITE, pg.Rect(win_width - 20, win_height - 20, 20,20))

def flash_targets(dlist, tlist, flash):
    """function to flash targets"""
    fixation_cross()
    if flash == True:
        for t in tlist:
            t.color = GREEN
            t.draw_circle(win)
            draw_square()
            flash = False
    else:
        for t in tlist:
            t.color = default_color
            t.draw_circle(win)
    for d in dlist:
        d.draw_circle(win)
    pg.display.update()
    return flash



def animate(dlist, tlist, mlist):
    """function to move or animate objects on screen"""
    #for d in dlist:
    #   for t in tlist:
    for m in mlist:
        m.detect_collision(mlist)
            #t.detect_collision(mlist)
            #d.draw_circle(win)
        m.draw_circle(win)
    pg.display.update()


def static_draw(mlist):
    """function for static object draw"""
    for obj in mlist:
        obj.draw_circle()


def fixation_cross(color=BLACK):
    """function to draw fixation cross"""
    start_x, end_x = ((win_width/2)-7, (win_height/2)) , ((win_width/2)+7, (win_height/2))
    start_y, end_y = (win_width/2, (win_height/2)-7), (win_width/2, (win_height/2)+7)
    pg.draw.line(win, color, start_x, end_x, 3)
    pg.draw.line(win, color, start_y, end_y, 3)


def fixation_screen(mlist):
    """function to present the fixation cross and the objects"""
    fixation_cross(BLACK)
    for obj in mlist:
        obj.draw_circle()
    pg.display.update()


def text_objects(text, color, textsize):
    """text object defining text"""
    msg = pg.font.SysFont("arial", textsize)
    text_surf = msg.render(text, True, color)
    return text_surf, text_surf.get_rect()  # - Returns the text surface and rect object


def msg_to_screen(text, textcolor, textsize, pos, display=win):
    """function to render message to screen centered"""
    text_surface, text_rect = text_objects(text, textcolor, textsize)  # - set variable for text rect object
    text_rect.center = pos
    display.blit(text_surface, text_rect)


def msg_to_screen_centered(text, textcolor, textsize, display=win):
    """function to render message to screen centered"""
    text_surface, text_rect = text_objects(text, textcolor, textsize)  # - set variable for text rect object
    text_rect.center = (win_width/2), (win_height/2)
    display.blit(text_surface, text_rect)


def multi_line_message(text, textsize, pos=((win_width-(win_width/10)), win_height), color=BLACK, display=win):
    """function to split text message to multiple lines and blit to display window."""
    # -- Make a list of strings split by the "\n", and each list contains words of that line as elements.
    #font = pg.font.SysFont("arial", textsize)
    #words = [word.split(" ") for word in text.splitlines()]
    too_big = True 

    # -- Get the width required to render an empty space
    #space_w = font.size(" ")[0]  # .size method returns dimension in width and height. [0] gets the width
    #max_w, max_h = ((win_width-(win_width/10)), win_height)
    #text_x, text_y = pos

    while too_big == True:
        font = pg.font.SysFont("arial", textsize)
        words = [word.split(" ") for word in text.splitlines()]
        space_w = font.size(" ")[0]  # .size method returns dimension in width and height. [0] gets the width
        max_w, max_h = ((win_width-(win_width/10)), win_height)
        text_x, text_y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, True, color)  # get surface for each word
                word_w, word_h = word_surface.get_size()  # get size for each word
                if text_x + word_w >= max_w:  # if the a word exceeds the line length limit
                    text_x = (win_width/10)  # reset the x
                    text_y += word_h  # start a new row
                display.blit(word_surface, (text_x, text_y))  # blit the text onto surface according to pos
                text_x += word_w + space_w  # force a space between each word
            text_x = (win_width/10)  # reset the x
            text_y += word_h  # start a new row
        if text_y <= win_height - 15:
            too_big = False
        else: 
            textsize -= 3 # if too big for display then shrink the textsize and try again
            win.fill(background_col)
    pg.display.flip()


def message_screen(message, num_targ, total, display=win):
    if message == "start":
        display.fill(background_col)
        multi_line_message(start_text(num_targ, total), med_font, ((win_width - (win_width / 10)), 120))
    if message == "not_selected_enough":
        msg_to_screen_centered("Select " + str(num_targ) + " circles!", BLACK, med_font)
    if message == "timeup":
        display.fill(background_col)
        msg_to_screen_centered("Time's up! Now resetting", BLACK, large_font)
        pg.display.flip()
    if message == "prac_finished":
        display.fill(background_col)
        multi_line_message(prac_finished_txt, med_font, ((win_width - (win_width / 10)), 120))
        pg.display.flip()
    if message == "exp_finished":
        display.fill(background_col)
        multi_line_message(experim_fin_txt, large_font, ((win_width - (win_width / 10)), 150))
        pg.display.flip()

def correct_txt(selected, total):
    win.fill(background_col)
    if selected == total:
        msg_to_screen_centered("Good! " + str(selected) +  " out of " + str(total) + " correct", BLACK, large_font)
    else:
        msg_to_screen_centered("Sorry... " + str(selected) +  " out of " + str(total) + " correct", BLACK, large_font)
    pg.display.flip()
    pg.time.delay((feedback_time + 1) * 1000)

def guide_screen(call, mlist, selected_targets_list, num_targ, total):
    if call == "start":
        win.fill(background_col)
        multi_line_message(start_text(num_targ, total), med_font, ((win_width - (win_width / 10)), 120))
        pg.display.flip()
    if call == "focus":
        win.fill(background_col)
        fixation_cross()
        multi_line_message(fix_text, med_font, ((win_width - (win_width / 10)), (win_height / 2 + 30)))
        pg.display.flip()
    if call == "present":
        win.fill(background_col)
        fixation_cross()
        static_draw(mlist)
        multi_line_message(present_text(num_targ, total), med_font, ((win_width - (win_width / 10)), (win_height / 2 + 30)))
        pg.display.flip()
    if call == "answer":
        static_draw(mlist)
        multi_line_message(submit_ans_txt, med_font, ((win_width - (win_width / 10)), (win_height / 2 + 30)))
        pg.display.flip()
    if call == "timeup":
        win.fill(background_col)
        multi_line_message(guide_timeup_txt, med_font, ((win_width - (win_width / 10)), (win_height / 2 + 30)))
        pg.display.flip()
    if call == "submitted":
        win.fill(background_col)
        msg_to_screen_centered(guide_submit_txt.format(len(selected_targets_list)), BLACK, large_font)
        pg.display.flip()
    if call == "finished":
        win.fill(background_col)
        multi_line_message(guide_fin_txt, med_font,((win_width - (win_width / 10)), 120))
        pg.display.flip()

def user_break_screen():
    win.fill(background_col)
    msg_to_screen_centered("You've Earned a Break!... Press F to continue", BLACK, large_font)
    pg.display.flip()
    wait_key()

def score_screen(score):
    win.fill(background_col)
    msg_to_screen_centered("Score: " + str(score), BLACK, large_font)
    pg.display.flip()
    pg.time.delay(3 * 1000)

def is_valid(num):
    if (num >= 48 and num <= 57) or (num >= 97 and num <= 122) or (num == 46):
        return True
    else:
        return False


def user_info(type):
    pg.mouse.set_visible(False)
    pg.display.flip()
    name = "" # prepping variables
    exit = False

    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE or event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN:
                    exit_key = event.key
                    exit = True
                elif event.key == pg.K_BACKSPACE or event.key == pg.K_DELETE:
                    name = name[:-1] #delete last letter
                elif is_valid(event.key):
                    if (pg.key.get_mods() & pg.KMOD_CAPS) or (pg.key.get_mods() & pg.KMOD_SHIFT):
                        name = name + chr(event.key).upper()
                    else:
                        name = name + chr(event.key)
        if exit == True:
            break
        win.fill(background_col) #display input
        multi_line_message(input_text() + type + name, large_font, ((win_width - (win_width / 10)), 120))

    if exit_key == pg.K_RETURN or exit_key == pg.K_KP_ENTER:
        return name # If the user enters then we proceed with game
    else: # otherwise we quit the game
        pg.quit()
        sys.exit()

def play_again_exp():
    response = user_info("Play again? (type \'y\' for yes or \'n\' for no): ")
    while True:
        if response.lower() == 'y':
            return True
        if response.lower() == 'n':
            return False
        response = user_info("Play again? (type \'y\' for yes or \'n\' for no): ")

def high_score_info(high_score):
    win.fill(background_col)
    msg_to_screen_centered("Current High Score: " + str(high_score), BLACK, large_font)
    pg.display.flip()
    pg.time.delay(3 * 1000)

def new_high_score(score):
    win.fill(background_col)
    msg_to_screen_centered("New High Score! Your score: " + str(score), GREEN, large_font)
    pg.display.flip()
    pg.time.delay(5 * 1000)

def mot_screen():
    win.fill(background_col)
    msg_to_screen_centered("Motion Object Tracking (press F to continue)", BLACK, large_font)
    pg.display.flip()
    wait_key()
#=======================================================================================
#=======================================================================================
#================================ NBACK MESSAGE SCREENS ================================
#=======================================================================================
#=======================================================================================

def guide_screen_nback(call):
    if call == "start":
        win.fill(background_col)
        multi_line_message(start_text_nback(), med_font, ((win_width - (win_width / 10)), 40))
        pg.display.flip()
    if call == "practice":
        win.fill(background_col)
        multi_line_message(practice_text, large_font,((win_width - (win_width / 10)), 120))
        pg.display.flip()
    if call == "finished":
        win.fill(background_col)
        multi_line_message(guide_fin_txt_nback, large_font,((win_width - (win_width / 10)), 120))
        pg.display.flip()
    
def correct_screen(n, correct, fa, total):
    n = str(n)
    win.fill(background_col)
    msg_to_screen_centered(str(correct) +  " out of " + str(total) + " " + "targets identified with " + str(fa) + " mis-clicks.", BLACK, large_font)
    pg.display.flip()
    pg.time.delay((feedback_time + 2) * 1000)

def n_back_screen(n):
    n = str(n)
    win.fill(background_col)
    msg_to_screen_centered("This is a " + n + "-back task.", BLACK, large_font)
    pg.display.flip()
    pg.time.delay((feedback_time + 1) * 1000)

def blank_screen():
    win.fill(background_col)
    pg.display.flip()
    pg.time.delay(2 * 1000)

def nback_screen():
    win.fill(background_col)
    msg_to_screen_centered("N-back Experiment (press F to continue)", BLACK, large_font)
    pg.display.flip()
    wait_key()
