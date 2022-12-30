# nback experiment
# lab streaming layer, bug tests, undertanding how to score correctness and false alarms
#
import pygame as pg
from messagescreens import *
from MOT_constants import *
import random
import math
import sys
import os
import scipy.stats as scip
from datetime import date

block_length = 10 # how many stimuli per block
sequence_size = 5 # number of balls per stimuli
stimulus_time = 3 * 1000 # how long each stimulus is on the screen for (ms)
real_blocks = 5 # maximum number of real blocks
prac_blocks = 2 # maximum number of practice blocks
buffer = 300 # number of pixels on each edge of screen to act as buffer

# == Defines the Objects (Balls) and their Properties ==
class obj:
    def __init__(self, default_color):
        # -- Radius of the circle objects
        self.radius = obj_radius

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

    def draw_circle(self, x, y, display= win):
        # -- Function to draw circle onto display
        pg.draw.circle(display, self.color, (x, y), self.radius)

# generates a game for an nback trial
def generate_game(n):
    game = {"n": n}
    return game

# randomly generates a number of n-back hits for a given trial
def number_of_hits(game):
    n = game["n"]
    max_hits = ((block_length - n) // 3)
    if max_hits > 0:
        hits = random.choice(range(max_hits))
        if hits == 0:
            hits = 1
    else:
        hits = 1
    return hits

# generates a sequence of balls (0 == white, 1 == black)
def generate_sequence():
    pattern = []
    for i in range(sequence_size):
        pattern.append(random.choice([0,1]))
    return pattern

# checks for conflicts arising from numbers being spaced n apart in index list...
# specifically that one index is n numbers ahead of another index...
# one index should not start where another ends
def conflict(index, n):
    length = len(index)
    for i in range(length - n):
        if index[i] + n in index: # if there is a repeat or one ends where the other begins, then there is a conflict
            return True
        for j in range(length):
            if (index[i] == index [j]) and (i != j):
                return True
    return False

# generates a list of the upcoming trial
def generate_n_back_trial(game):
    n = game["n"]
    hits = number_of_hits(game)
    repeats = [] # sequences we intend to repeat as nback hits
    index = [] # the locations of the first occurences nback hits
    sequence_list = [0] * block_length # all sequences to be shown in an nback trial

    index = random.sample(range(block_length - n), hits) # choose a given (hits) amount of numbers from an acceptable range
    while conflict(index, n): # make sure there are no conflicts with the numbers in index
        index = random.sample(range(block_length - n), hits)
    for i in range(hits): # generates the patterns that will be repeated
        repeats.append(generate_sequence())
    
    index_alt = index.copy() # create this so we can mess with index but also return the original index in the end
    repeats_alt = repeats.copy() #same deal as line above
    pattern = generate_sequence() # initialization
    while index_alt != []: # place the repeatd patterns into a sequence list for the trial
        sequence_list[index_alt[0]] = repeats_alt[0] # add target pattern at beginning index
        sequence_list[index_alt[0] + n] = repeats_alt[0] # add target pattern at end index
        del index_alt[0] # remove that index (so we may move to the next index)
        del repeats_alt[0] # remove that pattern (so we may move to the next pattern)
    for i in range(block_length): # fill in remaining spaces with random sequences
        if sequence_list[i] == 0:
            while pattern in repeats or pattern in sequence_list: # make sure it does not match any of the target patterns or other patterns. 
                pattern = generate_sequence()
            sequence_list[i] = pattern # once we have a unique pattern we add it to the list
    return index, sequence_list

# generates a screen of balls given a pattern
def generate_balls(pattern):
    balls = []
    for i in range(len(pattern)):
        if pattern[i] == 0:
            ball = obj(WHITE)
            balls.append(ball)
        if pattern[i] == 1:
            ball = obj(BLACK)
            balls.append(ball)
    return balls

# function for recording responses
def record_response(targs_identified, total_targs, nback_level, d_prime_value, log):
    # record the responses
    header_list = [targs_identified, total_targs, nback_level, d_prime_value]
    # convert to string
    header_str = map(str, header_list)
    # convert to a single line, separated by commas    
    header_line = ','.join(header_str)
    header_line += '\n'
    log.write(header_line)

# displays a given stimulus
def display_stimulus(pattern):
    range = abs(boundary["right"] - boundary["left"]) - (2 * (buffer + obj_radius)) # where we can draw balls
    step =  range / (sequence_size - 1) # step size for each ball
    starting_step = boundary["left"] + buffer + obj_radius # first ball starts where we want it to
    vertical_center = abs(boundary["up"] - boundary["down"]) / 2
    
    balls = generate_balls(pattern)
    win.fill(background_col)
    i = 0
    for ball in balls:
        ball.draw_circle(starting_step + (i * step), vertical_center)
        i += 1
    pg.display.flip()

# updates game, score, correct proportion and false alarm proportion
def level_change(index, responses, game, gametype, score, hit_rate, FA_rate):
    n = game["n"]
    correct = 0 # correct
    FA = 0 # false alarms
    # calculate correct
    for i in range(len(index)): # look at each index and see if user clicks button n trials later
        if responses[index[i] + n] == 1:
            correct += 1
    hit_rate.append(correct / len(index)) # calculates proportion correct out of actual targets

    for i in range(len(responses)): #record number of false alarms
        if (responses[i] == 1) and not (i in index):
            FA += 1
    FA_rate.append(FA / (block_length - len(index))) # calculates rate of false alarms as a proportion

    if gametype == "guide":
        game["n"] += 1
        return correct, FA, game, score

    if correct > 0.9: # success condition
        game["n"] += 1
        score += n # score increases by n
    elif correct < 0.5: # failure condition
        game["n"] -= 1
        score -= n // 2 # score decreases by n / 2 (floor function)
    else: # do nothing condition
        pass
    if game["n"] < 1:
        game["n"] = 1
    if score < 0:
        score = 0
    return correct, FA, game, score, hit_rate, FA_rate

def welcome_messages(game, gametype, high_score):
    if gametype == 'guide':
        guide_screen_nback("start", sequence_size)
        wait_key()

        # == Fixation cross screen ==
        guide_screen_nback("practice", sequence_size)
        wait_key()

    if gametype == 'real':
        high_score_info(high_score)

def end_messages(game, gametype, recorder):
    win.fill(background_col)
    if gametype == 'real':
        win.fill(background_col)
        multi_line_message(experim_fin_txt, large_font, ((win_width - (win_width / 10)), 150))
        pg.display.flip()
        wait_key()
        recorder.close()
    else:
        guide_screen_nback("finished", sequence_size)
        wait_key()

# function to prepare files for highscore, results, and grab highscore
def prepare_files():
    high_score = 0
    date_sys = str(date.today())
    observer = user_info("Observer: ")
    participant = user_info("Participant: ")

    if getattr(sys, 'frozen', False):
        # The application is frozen (is an executable)
        file_path = os.path.dirname(sys.executable)
    else:
        # The application is not frozen (is not an executable)
        file_path = os.path.dirname(__file__)


    NBACK_etc_path = os.path.join(file_path, "NBACK_etc")
    try: # create a folder for results and highscores if none exists
        os.mkdir(NBACK_etc_path)
    except:
        pass

    results_path = os.path.join(NBACK_etc_path, "Results_N-back_exp")

    try:
        os.mkdir(results_path)
    except: # if folder for results exists then do nothing, otherwise create such a folder
        pass
    
    highscore_path = os.path.join(NBACK_etc_path, "Highscore_N-back_exp")
    try:
        os.mkdir(highscore_path) 
    except: # if it does exist, then grab the high score
        with open(os.path.join(highscore_path,'highscores.txt')) as f:
            i = 0
            for line in f: # grabs highscore (last line in highscore file)
                if i == 0:
                    pass
                else:
                    high_score = int(line)
                i += 1
            f.close()
    else: # if no directory exists then create one and a highscore file
        f = open(os.path.join(highscore_path,'highscores.txt'), 'w')
        f.write('High Scores\n')
        f.close()
        f = open(os.path.join(highscore_path,'highscores.txt'), 'a')
        f.write("0\n")
        f.close()

    # == Prepare a CSV file for trial data ==
    mot_log = date_sys + ' pcpnt_' + participant + ' obsvr_' + observer +'.txt'
    filename = os.path.join(results_path, mot_log)
    log = open(filename, 'w')
    header = ["targets_identified", "total_targets", "n", "d-prime"]
    delim = ",".join(header)
    delim += "\n"
    log.write(delim)
    return log, highscore_path, high_score

# calculate a d-prime for a trial and update the overall list
def d_prime(hit_rate, FA_rate, dprimes):
    z_hit = scip.norm.pdf(len(hit_rate) - 1)
    print(str(z_hit))
    z_fa = scip.norm.pdf(len(FA_rate) - 1)
    print(str(z_fa))
    dp = z_hit - z_fa
    dprimes.append(dp)
    return dprimes

# runs trials (possible off by one errors.)
def trials(game, gametype, total_blocks, highscore, log):
    # initializing variables    
    # ==============================================================================================
    message_shown = False
    count = 0 
    completed_blocks = 0 
    score = 0 # initialization
    t0 = pg.time.get_ticks()
    submitted = False # keeps track of if a user submits on a given trial
    index, patterns_list = generate_n_back_trial(game)
    pattern = patterns_list[0]
    responses = [0] * block_length # keeps track of user responses (1 = affirmative and 0 = no response)
    hit_rate = []
    FA_rate = []
    dprimes = []
    # -================================================================================================
    welcome_messages(game, gametype,highscore) # welcome messages
    while True:
        t1 = pg.time.get_ticks()
        dt = t1 - t0 # update time
        if completed_blocks < total_blocks:
            # ========================================================
            # show screen indicating which level we are on (which n-back n we are using)
            if message_shown == False:
                n_back_screen(game) # display which task it is
                message_shown = True
                t0 = pg.time.get_ticks()
            # ========================================================
            elif count < block_length and message_shown == True:
                if dt <= stimulus_time: # displays a single stimulus
                    for event in pg.event.get(): # key control
                        if event.type == pg.QUIT:
                            pg.quit()
                            sys.exit()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_SPACE and submitted == False:
                                submitted = True # record key press 
                                responses[count] = 1 # user believes it is an nback target
                            elif event.key == pg.K_q or event.key == pg.K_ESCAPE:
                                if gametype == 'real':
                                    return score # quit the game
                                else:
                                    return True
                            elif event.key == pg.K_k: # allows you to skip to real trials
                                if gametype == 'guide':
                                    return False
                    display_stimulus(pattern)
                else: # switches stimulus
                    if submitted == False:
                        responses[count] = 0 # if user does not respond, then record their nonresponse
                    submitted = False
                    count += 1
                    blank_screen() # give blank screen before next stimulus
                    if count < block_length: # update to next pattern unless this is the last pattern
                        pattern = patterns_list[count]
                    t0 = pg.time.get_ticks() # reset time measure
            else: # reset for next block
                # =====================================
                # reseting variables
                completed_blocks += 1 
                count = 0
                submitted = False
                message_shown = False
                n = game['n']
                total = len(index) # total targets
                # =======================================
                if gametype == 'guide':
                    correct, FA, game, score = level_change(index, responses, game, gametype, score, hit_rate, FA_rate)
                else:
                    correct, FA, game, score, hit_rate, FA_rate = level_change(index, responses, game, gametype, score, hit_rate, FA_rate) # checks users performance (only based on correct hits, but should be generalizable to false alarms)
                #dprimes = d_prime(hit_rate, FA_rate, dprimes)
                if gametype == 'real':
                    record_response(correct, len(index), n, 0, log)
                    #record_response(correct, len(index), n, dprimes[len(dprimes) - 1], log) # will only save data from completed block!
                responses = [0] * block_length # reset responses
                index, patterns_list = generate_n_back_trial(game) # generates a new set of patterns and indices for targets
                pattern = patterns_list[count] # update pattern to first pattern from new set of patterns
                correct_screen(n, correct, total) # display how many targets the user hit
                if gametype == 'real': # display score if applicable
                    score_screen(score) # various message screens
        else: # quit game and give end message screens. 
            end_messages(game, gametype, log)
            if gametype == 'real':
                return score
            else:
                return False

def main():

    # == Initiate pygame and collect user information ==
    pg.init()
    log, highscore_path, high_score = prepare_files()

    # == Start guide/practice rounds  ==
    quit = trials(generate_game(1), "guide", prac_blocks, high_score, log)


    # == Start real trials, recording responses ==
    if not quit:
        score = trials(generate_game(6), "real", real_blocks, high_score, log)
    
    if score > high_score: # update high score if applicable
        f = open(os.path.join(highscore_path,'highscores.txt'), 'a')
        f.writelines(str(score) + '\n')
        f.close()
        new_high_score(score)
    pg.quit()  
    sys.exit()        
    
if __name__ == "__main__":
    main()