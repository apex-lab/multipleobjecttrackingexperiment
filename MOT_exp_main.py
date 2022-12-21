# ------------------------------------------------------------------------------------------------
# BUGS/things to edit/things to consider: 
# 1) add additional message screens (make level/stage premise more clear?).
# 2) code cleanliness (test lines, commenting format, redundencies, difficult to understand
#    variables,etc ...)
# 3) perhaps edit generate_list() so that we set a minimum velocity s.t. |min_vel| > 0
#  General Note: want to be addictive (think flow), not too boring and not too difficult
# 4) adding music to keeping people engaged (come up with ideas from playing alot, wait to implement) 
# 5) Incorportate Lab Streaming Layer functionality
# Note: MAKE EVERYTHING EASY TO CHANGE LATER
# ------------------------------------------------------------------------------------------------

# import pygame as pg
import sys
import random
import os
import scipy.stats as stats
import statistics
from messagescreens import  *
from psychopy.gui import DlgFromDict

# == Game Structure Variables ==
# == Attributes and relations between those attributes ==
attributes = ["targs", "speed", "dists"]
att_max = [3,3] 
# If you edit att_max then I reccomend keeping the first 
# entry as an odd number. The below code is some added functionality
# for determining how large the range of distractors around the 
# targets should be and it works better with odd numbers. I could
# go into detail on request, but I will save that and just say 
# that I reccomend using odd numbers. It still works with even numbers
# and will not break anything if you use an even one, just a reccomendation
scale = 1
dist_range = att_max[1] // 2
starting_targs = 3

# == how far player progresses or regresses based on performance ==
success = 1
failure = -3

# == Trial variables ==
real_time = 3.6 * (10 ** 6) # time that real trials last (milliseconds)
prac_trials = 2 # number of practice trials
guide_trials = 1 # number of guide trials

# == Processing power or frames per second ==
FPS = 144

# == Defines the Objects (Balls) and their Properties ==
class MOTobj:
    def __init__(self, game, default_color,):
        # -- Radius of the circle objects
        self.radius = obj_radius


        # -- Object positions attributes
        self.x, self.y = choice([n for n in range(int(boundary["left"]), int(boundary["right"]))
                                 if n not in range(x - self.radius, x + self.radius)]), \
                         choice([n for n in range(int(boundary["up"]), int(boundary["down"]))
                                 if n not in range(y - self.radius, y + self.radius)])
        
        # -- Velocity initialization (NOT 0)
        self.dx = 0
        self.dy = 0
        while (abs(self.dx) <= 0.1 or abs(self.dy) <= 0.1):
            self.dx = random.choice([-1,1]) * ((game["speed"])  + random.uniform(0, 1))
            self.dy = random.choice([-1,1]) * ((game["speed"]) + random.uniform(0, 1))

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
        # -- Return boolean value depending on mouse position, if it is in circle or not
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

    def draw_circle(self, display=win):
        # -- Function to draw circle onto display
        pg.draw.circle(display, self.color, (int(self.x), int(self.y)), self.radius)

    def draw_square(self, display=win):
        # -- Function to draw circle onto display
        pg.draw.rect(display, self.color, pg.Rect(win_width - 20, win_height - 20, 20,20))

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

    def shuffle_position(self):
        """Shuffle the position of circles"""
        self.x = choice([n for n in range(int(boundary["left"]), int(boundary["right"]))
                         if n not in range(x - self.radius, x + self.radius)])
        self.y = choice([n for n in range(int(boundary["up"]), int(boundary["down"]))
                         if n not in range(y - self.radius, y + self.radius)])


def velocity_change(self, game):
        self.dx = random.choice([-1,1]) * ((game["speed"])  + random.uniform(0, 1))
        self.dy = random.choice([-1,1]) * ((game["speed"]) + random.uniform(0, 1))
        while (abs(self.dx) <= 0.1 or abs(self.dy) <= 0.1):
            self.dx = random.choice([-1, 1]) * ((game["speed"])  + random.uniform(0, 1))
            self.dy = random.choice([-1,1]) * ((game["speed"]) + random.uniform(0, 1))
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
    return distractor_list, target_list


# == Helper Function for Delaying Game by t seconds ==
def delay(t):
    """function to stop all processes for a time"""
    pg.time.delay((t*1000))  # multiply by a thousand because the delay function takes milliseconds

# == Function for Recording User Performance ==
def record_response(d_prime, response_time, targs_identified, game, time_out_state, log):
    # record the responses
    header_list = [d_prime, response_time, targs_identified, game["targs"], game["stage"], time_out_state]
    # convert to string
    header_str = map(str, header_list)
    # convert to a single line, separated by commas
    if d_prime == 'NA':    
        header_line = ','.join(header_str)
        header_line += '\n'
    else:
        header_line = 'd\' = ' + str(d_prime)
    log.write(header_line)

# == plays proper welcome messages based on gametype ==
def welcome_messages(game, gametype):
    num_targs = game["targs"]
    num_dists = game["dists"]
    total = num_targs + num_dists
    
    if gametype == 'guide':
        wait_key()
        pg.display.flip()
        guide_screen("start", [], [], num_targs, total)
        wait_key()

        # == Fixation cross screen ==
        guide_screen("focus", [], [], num_targs, total)
        wait_key()

        # == Present cross and circles screen ==
        guide_screen("present", [], [], num_targs, total)
        wait_key()

# == plays proper end messages based on gametype ==
def end_messages(game, gametype, recorder):
    num_targs = game["targs"]
    num_dists = game["dists"]
    total = num_dists + num_targs
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
    if gametype == 'real' and tot_time % (6 * (10 ** 5)) == 0:
        return True
    return False

# == updates the score given current score and consecutive correct trials
def update_score(score, consecutive):
    return score + consecutive

def d_prime(hit_rate, FA_rate):
    # in this we use 1 for the thing we vary around for the hits
    # in this we use 0.5 for the thing we vary around for the false alarms
    # for both mean and standard deviation (z score = value - mean / std)
    # higher d' means better signal recognition
    std_hit = statistics.stdev(hit_rate, 1)
    std_fa = statistics.stdev(FA_rate, 0.5)
    if std_hit == 0:
        return 3
    else:    
        hit = (statistics.mean(hit_rate) - 1) / std_hit # calculates z score around mean of 1 (user knows what they are doing p = 1)
    if std_fa == 0:
        return -3
    else:    
        fa = (statistics.mean(FA_rate) - 0.5) / std_fa # calculates z score around mean of 1 (user is guessing p = 0.5)
    return hit - fa


# == Defines an object to flash in corner of screen for our photosensor ==
flash_square = MOTobj(update_game(0), WHITE) 

# == Runs Real Trials (same as practice but user performance is saved) ==
def trials(game, CRT, recorder, gametype, time_or_trials, hit_rate, FA_rate):
    tot_time = 0 # keeps track of how much time has passed
    # == Messages to user based on gametype ==
    welcome_messages(game, gametype)

    # == Generates the game ==
    list_d, list_t = generate_list(game, WHITE)
    list_m = list_d + list_t
    count = CRT
    flash = True
    reset = submitted = insufficient_selections = timeup = False
    score = consecutive = 0 # initializes score and consecutive correct trials
    t0 = pg.time.get_ticks()

    # == Controls the "game" part of the game ==
    while True:
        break_time = 0
        trial_time = pg.time.get_ticks() # keep track of trial length (including possible breaks)
        num_targs = game["targs"]
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
                if event.key == pg.K_ESCAPE: # what is going on here
                    if gametype == 'guide' or gametype == 'practice':
                        pg.quit()
                        sys.exit()
                    else:
                        return(game)
                if event.key == pg.K_SPACE:
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

        if count < time_or_trials:
            if not reset:
                if dt <= Tfix + 1:
                    pg.mouse.set_visible(False)
                    fixation_screen(list_m)
                elif Tfix + 1 < dt <= Tfl + 1.9:
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    pg.mouse.set_visible(False)
                    if flash == True:
                        flash = flash_targets(list_d, list_t, flash_square, flash) # flash color
                elif Tfl + 1.9 < dt <= Tfl + 2:
                    pg.mouse.set_visible(False)
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    flash_targets(list_d, list_t, flash_square, flash) # reset color
                elif Tfl + 2< dt <= Tani + 2:
                    pg.mouse.set_visible(False)
                    for targ in list_m: # hovering does not change color
                        targ.state_control("neutral")
                    animate(list_d, list_t, list_m)
                elif Tani + 2 < dt <= Tans+ 2:
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
                    t_stop = pg.time.get_ticks()
                elif Tans + 2 < dt:
                    pg.mouse.set_visible(False)
                    timeup = True

            if submitted: # -- if the user submits answers properly
                pg.mouse.set_visible(False)
                # == Records info for the trial ==
                if gametype == 'real':
                    hit_rate.append(len(selected_targ) / game["targs"]) # adding values to hit rate 
                    FA_rate.append((game["targs"] - len(selected_targ)) / game["targs"]) # adding values to false alarm rate
                    t_sub = ((t_keypress - t0)/1000) - animation_time
                    record_response("NA", t_sub, len(selected_targ), game, False, recorder)
                
                # == message screen stating performance on that trial ==
                win.fill(background_col)
                correct_txt(len(selected_targ), len(list_t))
                pg.display.flip()
                delay(feedback_time + 1)

                # == Based on that performance, we update the stage and score ==
                if len(selected_targ) == len(selected_list):
                    game["stage"] += success
                    consecutive += 1
                    score = update_score(score, consecutive)
                else:
                    game["stage"] += failure
                    consecutive = 0
                    if game["stage"] < 0:
                        game["stage"] = 0
                if gametype == 'real': 
                    score_screen(score) # display score

                reset = True

            if timeup: # -- if the user runs out of time
                pg.mouse.set_visible(False)
                if gametype == 'real':
                    record_response("NA", "timed out", "NA", game, True, recorder)
                message_screen("timeup", num_targs, num_targs + game["dists"])
                delay(feedback_time)
                count -= 1
                reset = True

            if reset: # -- prepare for the next trial
                pg.mouse.set_visible(False)
                if take_a_break(gametype, tot_time):
                # gives user break after certain amount of time and keeps track of length of break (not recorded)
                    break_time = pg.time.get_ticks()
                    user_break_screen(game)
                    break_time = pg.time.get_ticks() - break_time
                     
                game = update_game(game["stage"])
                list_d, list_t = generate_list(game, WHITE)
                #for i in range(len(list_d)):
                #    velocity_change(list_d[i], game)
                #for i in range(len(list_t)):
                #    velocity_change(list_t[i], game)
                list_m = list_d + list_t
                count += 1
                flash = True
                submitted = timeup = insufficient_selections= reset = False
                t0 = pg.time.get_ticks()

        else: # -- end oF experiment/practice/guide
            pg.mouse.set_visible(False)
            win.fill(background_col)
            end_messages(game, gametype, recorder)
            return (game)
        trial_time = pg.time.get_ticks() - trial_time
        tot_time = tot_time + trial_time - break_time # results in total gameplay time (not including breaks)


# == Main Loop  ==
def main():

    # == Variables to count how many trials have been completed ==
    completed_real_time = completed_practice_trials = completed_guide_trials = 0
    hit_rate = [] # hit rate for d' calculation
    FA_rate = [] # false alarm rate for d' calculation

    # == starting stages and levels ==
    game_guide = update_game(0)
    game_prac = update_game(0)
    game_real = update_game(0)
    

    # == Dialogue box to enter participant information ==
    dlg_box = DlgFromDict(session_info, title="Multiple Object Tracking", fixed=["date"])
    if dlg_box.OK:  # - If participant information has been entered

        # == Prepare a CSV file ==
        mot_log = date_string + ' pcpnt_' + session_info['Participant'] + '_obsvr_' + session_info['Observer']
        filename = save_path + mot_log +'.csv'
        log = open(filename, 'w')
        header = ["d_prime", "response_time", "targets_identified", "total_targets", "stage","timed_out"]
        delim = ",".join(header)
        delim += "\n"
        log.write(delim)

        # == Initiate pygame ==
        pg.init()
        pg.display.flip()

        # == Start guide ==
        trials(game_guide, completed_guide_trials, log, 'guide', guide_trials, hit_rate, FA_rate)

        # == Start practice ==
        trials(game_prac, completed_practice_trials, log, 'practice', prac_trials, hit_rate, FA_rate)

        # == Start real trials, recording responses ==
        game = trials(game_real, completed_real_time, log, 'real', real_time, hit_rate, FA_rate)
        dp = d_prime(hit_rate, FA_rate)
        record_response(dp, "NA","NA", game, False, log)
        pg.quit()
        sys.exit()

    else:  # - If the user has not entered the participant information
        print("User has cancelled")
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    main()
