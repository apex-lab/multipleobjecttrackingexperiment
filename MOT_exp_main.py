# ------------------------------------------------------------------------------------------------
# BUGS/things to edit/things to consider: 
# 1) add additional message screens (make level/stage premise more clear?).
# 2) code cleanliness (test lines, commenting format, redundencies, difficult to understand
#    variables, ...)
# 3) perhaps edit generate_list() so that we set a minimum velocity s.t. |min_vel| > 0
#  General Note: want to be addictive (think flow), not too boring and not too difficult
# 4) adding music to keeping people engaged (come up with ideas from playing alot, wait to implement) 
# 5) Incorportate Lab Streaming Layer functionality
# Note: MAKE EVERYTHING EASY TO CHANGE LATER
# ------------------------------------------------------------------------------------------------

# import pygame as pg
import sys
import random
from messagescreens import  *
from psychopy.gui import DlgFromDict

# == Game Structure Variables ==
# == Attributes and relations between those attributes ==
attributes = ["targs", "dists", "speed"]
att_max = [3,3] 
# If you edit att_max then I reccomend keeping the first 
# entry as an odd number. The below code is some added functionality
# for determining how large the range of distractors around the 
# targets should be and it works better with odd numbers. I could
# go into detail on request, but I will save that and just say 
# that I reccomend using odd numbers. It still works with even numbers
# and will not break anything if you use an even one, just a reccomendation
scale = 1
dist_range = att_max[0] // 2
starting_targs = 2

# == how far player progresses or regresses based on performance ==
success = 1
failure = -3

# == Trial variables ==
n_real = 25
n_prac = 2
n_guide = 1

# == Processing power or frames per second ==
FPS = 144

# == Defines the Objects (Balls) and their Properties ==
class MOTobj:
    def __init__(self, game, default_color=WHITE,):
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
        while (self.dx == 0 or self.dy == 0):
            self.dx = (game["speed"] + 1) * random.uniform(-1, 1)
            self.dy = (game["speed"] + 1) * random.uniform(-1, 1)

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

    def velocity_change(self,game):
        self.dx = (game["speed"] + 1)* random.uniform(-1, 1)
        self.dy = (game["speed"] + 1)* random.uniform(-1, 1)

# == returns product over elements up to entry n == 
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
def record_response(response_time, response_score, game, time_out_state, log):
    # record the responses
    header_list = [response_time, response_score, game["targs"], game["speed"], time_out_state]
    # convert to string
    header_str = map(str, header_list)
    # convert to a single line, separated by commas
    header_line = ','.join(header_str)
    header_line += '\n'
    log.write(header_line)

# == plays proper welcome messages based on gametype ==
def welcome_messages(game, gametype):
    num_targs = game["targs"]
    if gametype == 'real':    
        win.fill(background_col)
        msg_to_screen_centered(stage_txt(game), BLACK, large_font)
        pg.display.flip()
        delay(feedback_time + 2)
    
    if gametype == 'guide':
        wait_key()
        pg.display.flip()
        wait_key()
        pg.display.flip()
        guide_screen("start", [], [], num_targs)
        wait_key()

        # == Fixation cross screen ==
        guide_screen("focus", [], [], num_targs)
        wait_key()

        # == Present cross and circles screen ==
        guide_screen("present", [], [], num_targs)
        wait_key()

# == plays proper end messages based on gametype ==
def end_messages(game, gametype, recorder):
    num_targs = game["targs"]
    if gametype == 'real':
        message_screen("exp_finished", num_targs)
        pg.display.flip()
        wait_key()
        recorder.close()
    elif gametype == 'practice':
        message_screen("prac_finished", num_targs)
        pg.display.flip()
        wait_key()
    else:
        guide_screen("finished", [], [], num_targs)
        wait_key()

# == determines whether a user can take a break == 
def take_a_break(game,gametype):
    if gametype == 'real' and game["stage"] % 5 == 0 and game["stage"] != 0:
        return True
    return False

# == Defines an object to flash in corner of screen for our photosensor ==
flash_square = MOTobj(update_game(0), WHITE) 

# == Runs Real Trials (same as practice but user performance is saved) ==
def trials(game, CRT, recorder, gametype, tot_trials):

    # == Messages to user based on gametype ==
    welcome_messages(game, gametype)

    # == Generates the game ==
    list_d, list_t = generate_list(game, WHITE)
    list_m = list_d + list_t
    count = CRT
    reset = submitted = insufficient_selections = timeup = False
    t0 = pg.time.get_ticks()

    # == Controls the "game" part of the game ==
    while True:
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
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
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

        if count < tot_trials:
            if not reset:
                if dt <= Tfix + 1:
                    fixation_screen(list_m)
                elif Tfix + 1 < dt <= Tfl + 1:
                    flash_targets(list_d, list_t, flash_square)
                elif Tfl + 1< dt <= Tani + 1:
                    for targ in list_t:
                        targ.state_control("neutral")
                    for d in list_d:
                        d.state_control("neutral")
                    animate(list_d, list_t, list_m)
                elif Tani + 1 < dt <= Tans+ 1:
                    if insufficient_selections:
                        message_screen("not_selected_enough", num_targs)
                    if gametype == 'guide':
                        guide_screen("answer",list_m, selected_targ, num_targs)   
                    else: 
                        static_draw(list_m)
                    pg.display.flip()
                    t_stop = pg.time.get_ticks()
                elif Tans + 1 < dt:
                    timeup = True

            if submitted: # -- if the user submits answers properly
               
                # == Records info for the trial ==
                if gametype == 'real':
                    t_sub = ((t_keypress - t0)/1000) - animation_time
                    record_response(t_sub, len(selected_targ), game, False, recorder)
                
                # == message screen stating performance on that trial ==
                win.fill(background_col)
                msg_to_screen_centered("{:d} out of {:d} correct".format(len(selected_targ), len(selected_list)), BLACK, large_font)
                pg.display.flip()
                delay(feedback_time)

                # == Based on that performance, we update the stage ==
                if len(selected_targ) == len(selected_list):
                    game["stage"] += success
                else:
                    game["stage"] += failure
                    if game["stage"] < 0:
                        game["stage"] = 0

                # == Check if the user has earned a break ==
                if take_a_break(game, gametype):
                    user_break_screen(game)
                    delay(feedback_time + 2)
                reset = True

            if timeup: # -- if the user runs out of time
                if gametype == 'real':
                    record_response("timed out", "timed out", game, True, recorder)
                message_screen("timeup", num_targs)
                delay(feedback_time)
                count -= 1
                reset = True

            if reset: # -- prepare for the next trial
                game = update_game(game["stage"])
                list_d, list_t = generate_list(game, WHITE)
                list_m = list_d + list_t
                count += 1
                submitted = timeup = insufficient_selections= reset = False
                t0 = pg.time.get_ticks()

        else: # -- end of experiment/practice/guide
            win.fill(background_col)
            end_messages(game, gametype, recorder)
            break


# == Main Loop ==
def main():

    # == Variables to count how many trials have been completed ==
    completed_real_trials = completed_practice_trials = completed_guide_trials = 0

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
        header = ["response_time", "response_score", "stage", "level" ,"timed_out"]
        delim = ",".join(header)
        delim += "\n"
        log.write(delim)

        # == Initiate pygame ==
        pg.init()
        pg.display.flip()

        # == Start guide ==
        trials(game_guide, completed_guide_trials, log, 'guide', n_guide)

        # == Start practice ==
        trials(game_prac, completed_practice_trials, log, 'practice', n_prac)

        # == Start real trials, recording responses ==
        trials(game_real, completed_real_trials, log, 'real', n_real)
        pg.quit()
        sys.exit()

    else:  # - If the user has not entered the participant information
        print("User has cancelled")
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    main()
