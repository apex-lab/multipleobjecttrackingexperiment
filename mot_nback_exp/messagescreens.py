
#from psychopy import visual
from egi_pynetstation import NetStation
import pygame as pg
import os
from MOT_constants import *
import sys
#import pylsl

# == Set window ==
x, y = 50, 50
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
# = visual.window.Window(size=win_dimension, fullscr=True, winType='pygame')
win = pg.display.set_mode(win_dimension, pg.FULLSCREEN)
pg.display.set_caption(title)

# == Define colors. ==
background_col = GREY
hover_col = DARKSLATEGREY
click_col = GREENYELLOW
select_col = YELLOW

# Lab Streaming Layer push (pushes a string to the outlet)
#def LSL_push(outlet, string):
#    pylsl.StreamOutlet.push_sample(outlet, [string])

def draw_boundaries(display=win):
    #pg.draw.rect(display, BLACK, pg.Rect(win_width - boundary_size, 0, boundary_size, win_height - boundary_size)) # right
    pg.draw.rect(display, BLACK, pg.Rect(win_width - boundary_size, 0, boundary_size, win_height)) # right
    pg.draw.rect(display, BLACK, pg.Rect(0, 0, boundary_size, win_height)) # left
    pg.draw.rect(display, BLACK, pg.Rect(0, 0, win_width, boundary_size)) # top
    pg.draw.rect(display, BLACK, pg.Rect(0, win_height - boundary_size, win_width, boundary_size)) # bottom
    #pg.display.update()

def wait_key():
    """function to wait key press"""
    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == pg.K_f:
                return

def draw_square(outlet, tag, mlist, display=win):
        # -- Function to draw circle onto display
        #outlet.send_event(event_type = tag)
        pg.draw.rect(display, WHITE, pg.Rect(0, win_height - 20, 20,20))
        if tag == 'CLCK' or tag == 'UCLK' or tag == 'SPCE':
            static_draw(mlist)
        #pg.draw.rect(display, BLACK, pg.Rect(21, win_height - 20, win_width - 21,20))
        if tag == 'FLSH' or (tag[0] == 'F' and tag[1] == 'X'):
            pg.display.flip()
        else:    
            pg.display.update([pg.Rect(0, win_height - 20, 20,20), None])
        return pg.time.get_ticks()

def draw_square2(display=win):
        # -- Function to draw circle onto display
        pg.draw.rect(display, WHITE, pg.Rect(0, win_height - 20, 20,20))

def flash_targets(dlist, tlist, flash, gametype, outlet, flash_start_record):
    """function to flash targets"""
    play_sound = False
    fixation_cross()
    if flash == True:
        play_sound = True
        for t in tlist:
            t.color = GREEN
            t.draw_circle(win)
            flash = False
        if gametype == 'real':
            #draw_square(outlet, 'FLS', 0)
            pass
    else:
        for t in tlist:
            t.color = default_color
            t.draw_circle(win)
    for d in dlist:
        d.draw_circle(win)
    if flash_start_record == False: #and gametype == 'real': # record start of flash screen
        #LSL_push(outlet, 'FLSH0') # flash start
        draw_square(outlet, 'FLSH', 0)
        flash_start_record = True
    #else:
    #    if pg.time.get_ticks() - start_time < 200 and flash == False:
    #        draw_square2()
    pg.display.flip()
    return flash, flash_start_record

def animate(dlist, tlist, mlist, gametype, outlet, mvmt_start):
    """function to move or animate objects on screen"""
    for m in mlist:
        m.detect_collision(mlist)
        m.draw_circle(win)
        if mvmt_start == False: # and gametype == 'real':
            draw_square(outlet, 'MVE0', 0)
            #LSL_push(outlet, 'MVE') #start move
            mvmt_start = True
    pg.display.flip()
    return mvmt_start

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

def fixation_screen(mlist, gametype, outlet, fix_record, stage):
    """function to present the fixation cross and the objects"""
    fixation_cross(BLACK)
    for obj in mlist:
        obj.draw_circle()
    if fix_record == False: # and gametype == 'real' # record start of fixation screen
        level = stage + 1 # given the math, the level the user is on is the stage plus one
        fixation_tag = 'FX' + str(level) # add the level to the end of the string
        if len(fixation_tag) < 4: # if single digit, then add a trailing X
            fixation_tag = fixation_tag + 'X'
        draw_square(outlet, fixation_tag, 0)
        fix_record = True
        #LSL_push(outlet, 'FIX0') #fixation start
    pg.display.flip()
    return fix_record

def text_objects(text, color, textsize):
    """text object defining text"""
    msg = pg.font.SysFont("arial", textsize)
    text_surf = msg.render(text, True, color)
    return text_surf, text_surf.get_rect()  # - Returns the text surface and rect object

def msg_to_screen(text, textcolor, textsize, pos, display=win):
    """function to render message to screen centered"""
    text_surface, text_rect = text_objects(text, textcolor, textsize)  # - set variable for text rect object
    text_rect.center = pos
    draw_boundaries()
    display.blit(text_surface, text_rect)
    pg.display.flip()

def msg_to_screen_centered(text, textcolor, textsize, display=win):
    """function to render message to screen centered"""
    too_big = True
    text_x = 0
    max_w = win_width-(win_width/10)
    #while too_big == True:
    text_surface, text_rect = text_objects(text, textcolor, textsize)  # - set variable for text rect object
    text_rect.center = (win_width/2), (win_height/2)
    draw_boundaries()
    display.blit(text_surface, text_rect)
    pg.display.flip()
        #if text_x <= max_w:
         #   too_big = False

def multi_line_message(text, textsize, pos=((win_width-(win_width/10)), win_height), color=BLACK, display=win):
    """function to split text message to multiple lines and blit to display window."""
    # -- Make a list of strings split by the "\n", and each list contains words of that line as elements.
    #font = pg.font.SysFont("arial", textsize)
    #words = [word.split(" ") for word in text.splitlines()]
    too_big = True 
    final_text_x = 0

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
            final_text_x = text_x
            text_x = (win_width/10)  # reset the x
            text_y += word_h  # start a new row
        if text_y <= win_height - boundary_size - 20:
            too_big = False
        else: 
            textsize -= 3 # if too big for display then shrink the textsize and try again
            win.fill(background_col)
        draw_boundaries()
    pg.display.flip()

def message_screen(message, num_targ, total, display=win):
    if message == "start":
        display.fill(background_col)
        multi_line_message(start_text(num_targ, total), med_font, ((win_width - (win_width / 10)), 120))
    if message == "not_selected_enough":
        multi_line_message("Select " + str(num_targ) + " circles!", med_font, (win_width/2, win_height/2))
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

def stage_screen(stage):
    win.fill(background_col)
    msg_to_screen_centered("Level " + str(stage), BLACK, large_font)
    pg.display.flip()
    pg.time.delay(1500)

def correct_txt(selected, total, audio_path):
    win.fill(background_col)
    if selected == total:
        msg_to_screen_centered("Good! " + str(selected) +  " out of " + str(total) + " correct", BLACK, large_font)
    else:
        msg_to_screen_centered("Sorry... " + str(selected) +  " out of " + str(total) + " correct", BLACK, large_font)
    pg.display.flip()
                    # plays sounds
    if selected == total:
        pg.mixer.music.load(os.path.join(audio_path,'correct.mp3'))
    else:
        pg.mixer.music.load(os.path.join(audio_path,'incorrect.mp3'))
    pg.mixer.music.set_volume(0.22)
    pg.mixer.music.play()
    pg.time.delay(2000)
    pg.mixer.music.unload()

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
    pg.time.delay(1500)

def is_valid(num):
    if (num >= 48 and num <= 57) or (num >= 97 and num <= 122) or (num == 46) or (num == 32):
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

def high_score_info(high_scores):
    win.fill(background_col)
    multi_line_message(high_scores_info_txt(high_scores), large_font, ((win_width - (win_width / 10)), 40))
    pg.display.flip()
    pg.time.delay(5 * 1000)

def new_high_score(score, i):
    win.fill(background_col)
    msg_to_screen_centered("New High Score! You are now #" + str(i) + "! Your score: " + str(score), GREEN, med_font + 10)
    pg.display.flip()
    pg.time.delay(5 * 1000)

def final_score(score):
    win.fill(background_col)
    msg_to_screen_centered("Your Final score: " + str(score), BLACK, large_font)
    pg.display.flip()
    pg.time.delay(5 * 1000)

def mot_screen():
    win.fill(background_col)
    msg_to_screen_centered("Motion Object Tracking (press F to continue)", BLACK, large_font)
    pg.display.flip()
    wait_key()

# rest screen for collecting alpha wave data before/after the experiment
def rest_screen(outlet, num, audio_path):
    win.fill(background_col)
    draw_boundaries()
    multi_line_message("Please focus your eyes on the cross that will appear at the center of the screen.\n\n"\
                       "Do your best to keep your eyes still and your jaw/other muscles relaxed.\n\n" \
                        "Press F to begin this portion of the experiment whenever you are ready.", large_font, ((win_width - (win_width / 10)), 40))
    wait_key()

    # eyes open portion 
    eyes_open_start = pg.time.get_ticks()
    draw_square(outlet, "OPN" + str(num), [])
    while (pg.time.get_ticks() - eyes_open_start <= 180000):
        win.fill(background_col)
        draw_boundaries()
        fixation_cross()
        if pg.time.get_ticks() - eyes_open_start <= 100:
            draw_square2()
        pg.display.flip()
    eyes_open_stop = pg.time.get_ticks()
    draw_square(outlet, "OPN" + str(num + 1), [])
    while (pg.time.get_ticks() - eyes_open_stop < 100):
        win.fill(background_col)
        draw_boundaries()
        draw_square2()
        pg.display.flip()
    
    # eyes closed portion
    win.fill(background_col)
    draw_boundaries()
    multi_line_message("Please close your eyes and do your best not to fall asleep. \n\n" \
                       "Do your best to keep your eyes still and your jaw/other muscles relaxed. \n\n" \
                        "You will hear a noise when it is time for you to open your eyes. \n\n" \
                       "Press F to begin this portion of the experiment whenever you are ready. ", large_font, ((win_width - (win_width / 10)), 40))
    wait_key()
    eyes_closed_start = pg.time.get_ticks()
    draw_square(outlet, "CLS" + str(num), [])
    while (pg.time.get_ticks() - eyes_closed_start <= 180000):
        win.fill(background_col)
        draw_boundaries()
        fixation_cross()
        if pg.time.get_ticks() - eyes_closed_start <= 100:
            draw_square2()
        pg.display.flip()
    eyes_closed_stop = pg.time.get_ticks()
    draw_square(outlet, "CLS" + str(num + 1), [])
    while (pg.time.get_ticks() - eyes_closed_stop < 100):
        win.fill(background_col)
        draw_boundaries()
        draw_square2()
        pg.display.flip()
    pg.mixer.music.load(os.path.join(audio_path,'open_eyes.mp3'))
    pg.mixer.music.set_volume(0.22)
    pg.mixer.music.play()
    pg.time.delay(2000)
    pg.mixer.music.unload()
    return
        

# deprecated... turns out that we do not need it
def consent_screens():
    page = 1
    consented = False
    proceed = False
    while consented == False:
        win.fill(background_col)
        for event in pg.event.get():
            if proceed == True:
                if event.key == pg.K_RIGHT:
                    page = page + 1
            if event.key == pg.K_LEFT:
                page = page - 1
        if page <= 1:
            page = 1
            multi_line_message("This is a consent form message", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 2:
            multi_line_message("General info/Purpose text", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 3:
            multi_line_message("Procedures and time required", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 4:
            multi_line_message("Additional procedures info", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 5:
            multi_line_message("Financial info", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 6:
            multi_line_message("Risks and Benefits", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 7:
            multi_line_message("Confidentiality", large_font, ((win_width - (win_width / 10)), 40))
        elif page == 8:
            multi_line_message("Contacts & questions", large_font, ((win_width - (win_width / 10)), 40))
        else:
            page = 9
            multi_line_message("Consent", large_font, ((win_width - (win_width / 10)), 40))
        pg.mouse.set_visible(False)
        pg.display.flip()

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
