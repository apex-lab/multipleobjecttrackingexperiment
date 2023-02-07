# ------------------------------------------------------------------------------------------------
# BUGS/things to edit/things to consider: 
# 1) code cleanliness (test lines, commenting format, redundencies, difficult to understand
#    variables,etc ...)
#  General Note: want to be addictive (think flow), not too boring and not too difficult
# 2) Incorportate Lab Streaming Layer functionality
# Note: MAKE EVERYTHING EASY TO CHANGE LATER
# ------------------------------------------------------------------------------------------------

import pygame as pg
import sys
import random
import os
from scipy.special import comb
import scipy.stats as scip
import math
from messagescreens import  *
from datetime import *
import csv
import numpy as np
#from pylsl import StreamInfo, StreamOutlet 

# == Game Structure Variables ==
# == Attributes and relations between those attributes ==
attributes = ["targs", "speed", "dists"]
att_max = [3,3] 
scale = 1
dist_range = att_max[1] // 2
starting_targs = 2

# == how far player progresses or regresses based on performance ==
success = 1
failure = -3

# == Trial variables ==
real_time = 1.2 * (10 ** 6) # time that real trials last (milliseconds)
prac_trials = 2 # number of practice trials
guide_trials = 1 # number of guide trials

# == Processing power or frames per second ==
FPS = 144

# == Defines the Objects (Balls) and their Properties ==
class MOTobj:
    def __init__(self, game, default_color):
        # -- Radius of the circle objects
        self.radius = obj_radius

        # -- Object positions attributes
        self.x, self.y = choice([n for n in range(int(boundary["left"]), int(boundary["right"]))
                                 if n not in range(x - self.radius, x + self.radius)]), \
                        choice([n for n in range(int(boundary["up"]), int(boundary["down"]))
                                 if n not in range(y - self.radius, y + self.radius)])

        #while (self.x > (boundary["right"] - 20 - self.radius)) and (self.y < (boundary["down"] + 20 + self.radius)):
        #    self.x, self.y = choice([n for n in range(int(boundary["left"]), int(boundary["right"]))
        #                         if n not in range(x - self.radius, x + self.radius)]), \
        #                choice([n for n in range(int(boundary["up"]), int(boundary["down"]))
        #                         if n not in range(y - self.radius, y + self.radius)])    
        
        # -- Velocity initialization
        self.dx, self.dy = velocity(game)

        # -- Set the circle object neutral state color
        self.color = default_color
        self.default_color = default_color

        # -- Timer attributes
        self.timer = 0
        self.flash = True

        # -- State attributes for mouse selection control
        self.state = ""
        self.isClicked = False
        self.isSelected = False
    
    def change_color(self, color):
        self.color = color

    def in_circle(self, mouse_x, mouse_y):
        # -- Return boolean value deping on mouse position, if it is in circle or not
        if math.sqrt(((mouse_x - self.x) ** 2) + ((mouse_y - self.y) ** 2)) < self.radius:
            return True
        else:
            return False

    def state_control(self, state):
        # -- Neutral or default state with no form of mouse selection
        if state == "neutral":
            self.color = self.default_color
            self.state = "neutral"
            self.isClicked = self.isSelected = False
        # -- Hovered state if mouse is hovering over circle object
        if state == "hovered":
            self.color = hover_col
            self.state = "hovered"
            self.isClicked = self.isSelected = False
        # -- Clicked state if mouse click DOWN while in object
        if state == "clicked":
            self.color = click_col
            self.state = "clicked"
            self.isClicked = True
            self.isSelected = False
        # -- Selected state if mouse click UP on a "clicked" object
        if state == "selected":
            self.color = select_col
            self.state = "selected"
            self.isClicked = False
            self.isSelected = True

    def draw_circle(self, display=win):
        # -- Function to draw circle onto display
        pg.draw.circle(display, self.color, (int(self.x), int(self.y)), self.radius)
        
    # add a fix for when dx/dy equals 0 (probably in brownian motion)
    def detect_collision(self, mlist):
        # -- Object positions in x and y coordinates change in velocity value
        self.x += self.dx
        self.y += self.dy
        # -- If the object reaches the window boundary, bounce back
        if self.x < self.radius or self.x > win_width-self.radius:
            self.dx *= -1
        if self.y < self.radius or self.y > win_height-self.radius:
            self.dy *= -1
        # -- If the object bounces off each other, run the Brownian motion physics
        # objects need to be from the same list, otherwise the objects
        # can pass through each other if they're from a different list
        for a in mlist:
            for b in mlist:
                if a != b:
                    if math.sqrt(((a.x - b.x) ** 2) + ((a.y - b.y) ** 2)) <= (a.radius + b.radius):
                        brownian_motion(a, b)

    def flash_color(self, issquare):
        # -- Function to flash color
        if self.timer == FPS:
            self.timer = 0
            self.flash = not self.flash

        self.timer += 3

        if self.flash:
            self.color = self.default_color
        else:
            if issquare:
                self.color = GREY
            else:
                self.color = GREEN

# NEW NEW NEW randomly shuffles positions of balls
def shuffle_positions(mlist):
    """Shuffle the position of circles"""
    for self in mlist:
        self.x = choice([n for n in range(int(boundary["left"]), int(boundary["right"]))
                         if n not in range(x - self.radius, x + self.radius)])
        self.y = choice([n for n in range(int(boundary["up"]), int(boundary["down"]))
                         if n not in range(y - self.radius, y + self.radius)])

# NEW NEW NEW checks that balls do not spawn in corner or overlap, fixes problem if it occurs
def valid_positions(mlist):
    truth_list = []
    valid_positions = False 
    while (valid_positions == False):
        for m in mlist: # iterate over all balls 
            if (m.x > (boundary["right"] - 25 - m.radius)) and (m.y < (boundary["down"] + 25 + m.radius)):
                truth_list.append(0) # if located in corner with square then invalid
            for k in mlist:
                distance = math.sqrt(((m.x - k.x) ** 2) + ((m.y - k.y) ** 2))
                if distance < 2 * m.radius and distance != 0:
                    truth_list.append(0) # if overlapping with another ball then invalid
        if truth_list == []: # if every ball satisfies our condition then we are fine 
            valid_positions = True
        else: #otherwise we shuffle the balls and start again
            shuffle_positions(mlist)
        truth_list = []
    
# get initial dx and dy values for balls
def velocity(game):
    speed = game["speed"]
    overall_velocity = math.sqrt(2 * ((speed + 2.75) ** 2))
    dx = random.choice([-1,1]) * random.uniform(0, overall_velocity)
    dy = random.choice([-1,1]) * math.sqrt((overall_velocity ** 2) - (dx ** 2))
    return dx, dy

# == returns product over elements up to and including entry n == 
def product(list, n):
    prod = 1
    for i in range(n):
        if list[len(list)- i - 1] != 0:
            prod *= list[len(list)- i - 1]
    return prod

# == Function for updating a game based on the stage ==
# -- Defines a dictionary called "game"
def update_game(stage):
    if stage < 0:
        stage = 0
    game = {"stage": stage}
    i = 0
    for att in attributes:
        prod = product(att_max, len(att_max) - i)
        if i == len(att_max):
            game[att] = stage
        elif stage >= prod:
            game[att] = stage // prod
            stage -= game[att] * prod
        else:
            game[att] = 0
        i += 1
    game["targs"] += starting_targs
    game["dists"] = game["targs"] - scale * (dist_range - game["dists"])
    if game["dists"] == 0:
        game["dists"] += 1
    return game

# == Generates a List of Objects (Balls) ==
def generate_list(game, color):
    """function to generate new list of objects"""
    target_list = []
    num_targ = game["targs"]
    for nt in range(num_targ):
        t = MOTobj(game, color)
        target_list.append(t)

    distractor_list = []
    num_dist = game["dists"] 
    for nd in range(num_dist):
        d = MOTobj(game, color)
        distractor_list.append(d)
    mlist = distractor_list + target_list # NEW NEw NEW 
    valid_positions(mlist) # NEW NEW NEW after balls for trial generated we make sure they occupy valid positions 
    return distractor_list, target_list

# == Helper Function for Delaying Game by t seconds ==
def delay(t):
    """function to stop all processes for a time"""
    pg.time.delay((t*1000))  # multiply by a thousand because the delay function takes milliseconds

# == Function for Recording User Performance ==
def record_response(participant_number, user_number, name, response_time, targs_identified, game, time_out_state, d_prime, total_time, log):
    # record the responses
    header_list = [participant_number, user_number, name, response_time, targs_identified, game["targs"], game["stage"], time_out_state, d_prime, total_time]
    # convert to string
    header_str = map(str, header_list)
    # convert to a single line, separated by commas    
    header_line = ','.join(header_str)
    header_line += '\n'
    log.write(header_line)

# == plays proper welcome messages based on gametype ==
def welcome_messages(game, gametype, high_score):
    num_targs = game["targs"]
    num_dists = game["dists"]
    total = num_targs + num_dists
    
    if gametype == 'guide':
        guide_screen("start", [], [], num_targs, total)
        wait_key()

        # == Fixation cross screen ==
        guide_screen("focus", [], [], num_targs, total)
        wait_key()

        # == Present cross and circles screen ==
        guide_screen("present", [], [], num_targs, total)
        wait_key()
    if gametype == 'real':
        high_score_info(high_score)
        stage_screen(game["stage"] + 1)

# == plays proper end messages based on gametype ==
def end_messages(game, gametype, recorder):
    num_targs = game["targs"]
    num_dists = game["dists"]
    total = num_dists + num_targs
    win.fill(background_col)
    if gametype == 'real':
        message_screen("exp_finished", num_targs, total)
        pg.display.flip()
        wait_key()
        recorder.close()
    elif gametype == 'practice':
        message_screen("prac_finished", num_targs, total)
        pg.display.flip()
        wait_key()
    else:
        guide_screen("finished", [], [], num_targs, total)
        wait_key()

# == determines whether a user can take a break == 
def take_a_break(gametype, tot_time):
    if gametype == 'real' and tot_time > (6 * (10 ** 5)):
        return True
    return False

# == updates the score given current score and consecutive correct trials
def update_score(score, consecutive, stage):
    return score + consecutive + math.floor(stage / 2)

# == function for calculating expected balls correct on a trial if user were guessing
def expected_value(game):
    targs = game["targs"]
    total = targs + game["dists"]
    EV = 0
    for i in range(targs + 1):
        numerator = comb(targs, i) * comb(total - targs, targs - i)
        denominator = comb(total, targs) #combinatorial calculation
        EV += i * (numerator / denominator)
    return EV

# == calculates d-prime value ==
def d_prime(dprimes, hit_rate, game):
    total_targs = game["targs"]
    total_balls = game["targs"] + game["dists"]

    hits = round(hit_rate[-1] * total_targs) # calculate targets correctly identified
    misses = total_targs - hits # total misses (which in MOT is equivalent to false alarms)
    farate = misses / (total_balls - total_targs)
    correct_rejections = (total_balls - total_targs) - misses # number of correct rejections

    # values for fixing extreme d primes
    half_hit = 0.5 / (hits + misses)
    half_fa = 0.5 / (misses + correct_rejections)
    # fix extreme hit rate
    hitrate = hit_rate[-1]
    if hitrate == 1:
        hitrate = 1 - half_hit
    if hitrate == 0:
        hitrate = half_hit

    # fix extreme fa rate
    if farate == 1:
        farate = 1 - half_fa
    if farate == 0:
        farate = half_fa

    # calculate z values
    z_hit = scip.norm.ppf(hitrate)
    z_fa = scip.norm.ppf(farate)

    dp = z_hit - z_fa # calculate d prime
    dprimes.append(dp) # add to list
    return dprimes

def update_stage(selected_targ, game, gametype, score, consecutive):
    if len(selected_targ) == game["targs"]:
        game["stage"] += success
        consecutive += 1
        score = update_score(score, consecutive, game["stage"])
    else:
        game["stage"] += failure
        consecutive = math.floor(consecutive / 2)
        if game["stage"] < 0:
            game["stage"] = 0
    if gametype == 'real': 
        score_screen(score) # display score
    return game, score, consecutive

# == prepares where we store data such as results and high scores ==
def prepare_files():
    participant_number = 1
    high_score = [0] * 5 # get top 5 high scores
    date_sys = str(date.today())
    user_number = user_info("User Number: ")
    name = user_info("Full Name (Please enter your name exactly [e.g. 'John Doe']): ").lower()

    if getattr(sys, 'frozen', False): 
        # The application is frozen (is an executable)
        file_path = os.path.dirname(sys.executable)
    else:
        # The application is not frozen (is not an executable)
        file_path = os.path.dirname(__file__)
    
    MOT_etc_path = os.path.join(file_path, "MOT_etc")
    try: # create a folder for results and highscores if none exists
        os.mkdir(MOT_etc_path)
    except:
        pass
    results_path = os.path.join(MOT_etc_path, "Results_MOT_exp")

    try:
        os.mkdir(results_path)
    except: # if folder for results exists then do nothing, otherwise create such a folder
        pass
    
    highscore_path = os.path.join(MOT_etc_path, "Highscore_MOT_exp")
    try:
        os.mkdir(highscore_path) 
    except: # if it does exist, then grab the high score
        with open(os.path.join(highscore_path,'highscores.csv')) as f:
            i = 0
            for line in f: # grabs highscore (last line in highscore file)
                if i == 0:
                    pass
                else:
                    if int(line) > high_score[4]:
                        high_score.append(int(line))
                        high_score.sort(reverse=True) 
                i += 1
            f.close()
    else: # if no directory exists then create one and a highscore file
        f = open(os.path.join(highscore_path,'highscores.csv'), 'w')
        f.write('High Scores\n')
        f.close()
        f = open(os.path.join(highscore_path,'highscores.csv'), 'a')
        f.write("0\n")
        f.close()

    # Creating one big csv file for all user data
    results_csv_path = os.path.join(results_path, 'results.csv')
    if not (os.path.isfile(results_csv_path)): # if it doesn't exist, then create a file
        log = open(results_csv_path, 'w')
        header = ["participant number", "user number (for Lauren)", "name", "response_time","targets_identified","total_targets","stage","timed_out","d_prime", "total_time"]
        delim = ",".join(header)
        delim += "\n"
        log.write(delim)
    else: # if exists, then get new participant number
        log = open(results_csv_path, 'r') 
        i = 0
        for row in csv.reader(log): # grabs last participant number (last line, first entry)
            if i == 0:
                pass
            else:
                participant_number = int(row[0])
            i += 1
        participant_number += 1 # get the very next participant number
    log.close()
    log = open(results_csv_path, 'a')
    audio_path = os.path.join(file_path, 'Sound')
    return log, highscore_path, high_score, user_number, name, date_sys, audio_path, participant_number, results_path

# == Runs Real Trials (same as practice but user performance is saved) ==
def trials(game, recorder, gametype, time_or_trials, high_score, audio_path, participant_number, user_number, name): #, outlet):
    tot_time = 0 # keeps track of how much time has passed
    # == Messages to user based on gametype ==
    welcome_messages(game, gametype, high_score)

    # == Generates the game ==
    hit_rates = []
    dprimes = []
    list_d, list_t = generate_list(game, WHITE)
    list_m = list_d + list_t
    count = 0
    flash = True
    reset = False
    submitted = False
    highest_level = 0
    sound_played = False
    insufficient_selections = False # whole lot of initiating variables in this area
    timeup = False
    score = consecutive = 0 # initializes score and consecutive correct trials
    t0 = total_time = start_time = pg.time.get_ticks()

    # == Controls the "game" part of the game ==
    while True:
        trial_time = pg.time.get_ticks() # keep track of trial length (including possible breaks)
        num_targs = game["targs"]
        pushed_flash_already = False
        pushed_motion_already = False
        pg.time.Clock().tick_busy_loop(FPS)  # = Set FPS

        win.fill(background_col)  # - fill background with background color
        mx, my = pg.mouse.get_pos()  # - get x and y coord of mouse cursor on window

        selected_list = []  # - list for all selected objects
        selected_targ = []  # - list for all SELECTED TARGETS

        # == Controls responses to user input ===
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_k and (gametype == 'guide' or gametype == 'practice'):
                    return 'k'
                if event.key == pg.K_ESCAPE: # what is going on here
                    if gametype == 'real':
                        #outlet.push_sample(['esc'])
                        return score, dprimes, (game["stage"] + 1), (highest_level + 1)
                    else:
                        return 'esc'
                if event.key == pg.K_SPACE:
                    if gametype == 'real':    
                        #outlet.push_sample(['space'])
                        pass
                    if not reset:
                        for target in list_t:
                            if target.isSelected and not target.isClicked:
                                selected_targ.append(target)
                                selected_list.append(target)
                        for distractor in list_d:
                            if distractor.isSelected and not distractor.isClicked:
                                selected_list.append(distractor)
                        if len(selected_list) == num_targs:
                            submitted = True
                            t_keypress = pg.time.get_ticks()
                        else:
                            insufficient_selections = True
            for obj in list_m:
                if obj.in_circle(mx, my):
                    if event.type == pg.MOUSEMOTION:
                        if not obj.isClicked and not obj.isSelected:
                            obj.state_control("hovered")
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if gametype == 'real':    
                            #outlet.push_sample(['click'])
                            pass
                        if not obj.isClicked and not obj.isSelected:
                            obj.state_control("clicked")
                        if not obj.isClicked and obj.isSelected:
                            obj.state_control("neutral")
                    if event.type == pg.MOUSEBUTTONUP:
                        if obj.isClicked and not obj.isSelected:
                            obj.state_control("selected")
                elif not obj.in_circle(mx, my):
                    if event.type == pg.MOUSEMOTION:
                        if not obj.isClicked and not obj.isSelected:
                            obj.state_control("neutral")
                    if event.type == pg.MOUSEBUTTONUP:
                        if obj.isClicked and not obj.isSelected:
                            obj.state_control("neutral")

        # == Grabs the time after each frame and total time passed in the trial ==
        t1 = pg.time.get_ticks()
        dt = (t1 - t0)/1000

        if count < time_or_trials: # need to edit because we are using time for real trials
            if not reset:
                if dt <= Tfix + 1:
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    pg.mouse.set_visible(False)
                    fixation_screen(list_m)
                elif Tfix + 1 < dt <= Tfl + 1.95:
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    if flash == True:
                        if gametype == 'real':
                            #outlet.push_sample(['flash_start'])
                            pass
                        flash = flash_targets(list_d, list_t, flash) # flash color
                        dt = Tfl + 1.95
                elif Tfl + 1.95 < dt <= Tfl + 2:
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    if gametype == 'real' and pushed_flash_already == False:
                        #outlet.push_sample(['flash_stop'])
                        pushed_flash_already = True
                    flash_targets(list_d, list_t, flash) # reset color
                elif Tfl + 2 < dt <= Tani + 2:
                    pushed_flash_already = False
                    if gametype == 'real' and pushed_motion_already == False:
                        #outlet.push_sample(['move_start'])
                        pushed_motion_already = True
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    animate(list_d, list_t, list_m)
                elif Tani + 2 < dt <= Tans+ 2:
                    if gametype == 'real' and pushed_motion_already == True:
                        #outlet.push_sample(['move_stop'])
                        pushed_motion_already = False 
                    if Tani + 2 < dt <= Tani + 2.05: # reset mouse position
                        pg.mouse.set_pos([960,540])
                    pg.mouse.set_visible(True)
                    if insufficient_selections:
                        message_screen("not_selected_enough", num_targs, num_targs + game["dists"])
                    if gametype == 'guide':
                        guide_screen("answer",list_m, selected_targ, num_targs, num_targs + game["dists"])   
                    else: 
                        static_draw(list_m)
                    pg.display.flip()
                elif Tans + 2 < dt:
                    pg.mouse.set_visible(False)
                    timeup = True

            if submitted: # -- if the user submits answers properly
                total_time = (pg.time.get_ticks() - start_time) / 1000
                # == message screen stating performance on that trial ==
                pg.mouse.set_visible(False)
                correct_txt(len(selected_targ), len(list_t), audio_path)
                pg.mouse.set_visible(False)

                                # == Records info for the trial ==
                if gametype == 'real':
                    hit_rates.append(len(selected_targ) / len(selected_list))
                    dprimes = d_prime(dprimes, hit_rates, game)
                    t_sub = ((t_keypress - t0)/1000) - animation_time
                    record_response(participant_number, user_number, name, t_sub, len(selected_targ), game, False, dprimes[-1], total_time, recorder)

                # == Based on that performance, we update the stage and score ==
                game, score, consecutive = update_stage(selected_targ, game, gametype, score, consecutive)
                if game["stage"] > highest_level:
                    highest_level = game["stage"]
                reset = True

            if timeup: # -- if the user runs out of time
                total_time = (pg.time.get_ticks() - start_time) / 1000
                pg.mouse.set_visible(False)
                if gametype == 'real':
                    record_response(participant_number, user_number, name, "timed out", "NA", game, True, "NA", total_time, recorder)
                message_screen("timeup", num_targs, num_targs + game["dists"])
                delay(feedback_time)
                count -= 1
                reset = True

            if reset: # -- prepare for the next trial
                pg.mouse.set_visible(False)
                # gives user break after certain amount of time
                if take_a_break(gametype, tot_time):
                    user_break_screen()  
                    tot_time = 0

                game = update_game(game["stage"])
                list_d, list_t = generate_list(game, WHITE)
                list_m = list_d + list_t
                if gametype != 'real':
                    count += 1
                flash = True
                submitted = timeup = insufficient_selections= reset = sound_played = False
                if gametype == 'real':
                    stage_screen(game["stage"] + 1)
                t0 = pg.time.get_ticks()

        else: # -- end of experiment/practice/guide
            pg.mouse.set_visible(False)
            end_messages(game, gametype, recorder)
            if gametype == 'real':
                recorder.close()
                return score, dprimes, (game["stage"] + 1), (highest_level + 1)
            else:
                return "complete" # signifies succesful completion of prac/guide trials
        

        # total gameplay time (for use in giving users a break)
        trial_time = pg.time.get_ticks() - trial_time
        tot_time += trial_time 

# == Main Loop.  ==
def main(unified):
    mot_play_again = True
    while mot_play_again == True:
        # == Initiate pygame and collect user information ==
        #consent_screens()
        now = datetime.now()
        time = now.strftime("%H:%M:%S") # get current time
        pg.init()
        pg.mixer.init()
        log, highscore_path, high_score, user_number, name, date_sys, audio_path, participant_number, results_path = prepare_files()
    
        # prepare lab streaming layer functionality
        #info = StreamInfo('MOT_stream', 'Markers', 1, 0, 'string', '_Obs_' + observer + '_ptcpt_' + participant + '_' + date_sys + '_' + time)
        #outlet = StreamOutlet(info)

        game_guide = update_game(0)
        game_prac = update_game(0)
        game_real = update_game(0)
    
        # == Start guide ==
        key = trials(game_guide, log, 'guide', guide_trials, high_score, audio_path, participant_number, user_number, name)#, outlet)

        # == Start practice ==
        if key == 'k' or key == 'complete':
            key = trials(game_prac, log, 'practice', prac_trials, high_score, audio_path, participant_number, user_number, name)#, outlet)

        # == Start real trials, recording responses ==
        if key == 'k' or key == 'complete':
            score, dprimes, last_level, highest_level = trials(game_real, log, 'real', real_time, high_score, audio_path, participant_number, user_number, name)#, outlet)
        else:
            score = 0
    
        if score > high_score[4]: # update high score if applicable  
            i = 4
            while (score > high_score[i]) and (i >= 0): # calculate where on the highscore list it goes
                i = i - 1
            i += 2 # do this because we index from zero

            f = open(os.path.join(highscore_path,'highscores.csv'), 'a')
            f.writelines(str(score) + '\n')
            f.close()
            new_high_score(score, i)
        else:
            final_score(score)

        summary_csv_path = os.path.join(results_path, 'summary.csv')
        if not (os.path.isfile(summary_csv_path)): # if it doesn't exist, then create a file
            f = open(summary_csv_path, 'w')
            header = ["participant number", " user_number (for Lauren)", " name", " dprime_avg", " dprime_std", " highest_level_obtained", " last_level", " score"]
            delim = ",".join(header)
            delim += "\n"
            f.write(delim)
            f.close()
        f = open(summary_csv_path, 'a')
            # record the responses
        try:
            header_list = [participant_number, user_number, name, np.nanmean(dprimes), np.nanstd(dprimes), highest_level, last_level, score]
        except:
            header_list = [participant_number, user_number, name, "NaN", "NaN", "NaN", "NaN", "NaN"]
        # convert to string
        header_str = map(str, header_list)
        # convert to a single line, separated by commas    
        header_line = ','.join(header_str)
        header_line += '\n'
        f.write(header_line)
        f.close()





        # allow user to play again without rerunning program
        pg.mixer.quit()
        mot_play_again = play_again_exp()
        if mot_play_again == True:
            if unified == True:
                return True
        else:
            if unified == True:
                return False
            else:
                pg.quit()
                sys.exit()

if __name__ == "__main__":
    main(False)
