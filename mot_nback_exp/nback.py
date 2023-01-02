# nback experiment
# lab streaming layer, bug tests, undertanding how to score correctness and false alarms
#
import pygame as pg
from messagescreens import *
from MOT_constants import *
import random
import sys
import os
import scipy.stats as scip
from datetime import *
from pylsl import StreamInfo, StreamOutlet 

block_length = 15 # how many stimuli per block
stimulus_time = 3 * 1000 # how long each stimulus is on the screen for (ms)
real_blocks = 5 # maximum number of real blocks
prac_blocks = 2 # maximum number of practice blocks


# randomly generates a number of n-back hits for a given trial
def number_of_hits(n):
    max_hits = ((block_length - n - 1) // 2)
    if max_hits > 0:
        hits = random.choice(range(1, max_hits + 1))
    else:
        hits = 1
    return hits

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

# generates a list of letters for the upcoming trial
def generate_trial(n):
    hits = number_of_hits(n) # get a certain amount of targets
    index = [] # locations of first part of nback pair
    repeats = [] # the letters to be repeated
    sequence_list = [0] * block_length # prepare the overall list of letters

    index = random.sample(range(block_length - n), hits) # choose a hits number of hits from an acceptable range
    while conflict(index,n): # make sure there are no conflicts
        index = random.sample(range(block_length - n), hits)
    for i in range(hits): # generates the sequence of letters to be repeated as targets
        repeats.append(chr(random.choice(range(65,91))))

    index_alt = index.copy() # create this so we can mess with index but also return the original index in the end
    repeats_alt = repeats.copy() # same deal as line above
    letter = chr(random.choice((range(65,91))))
    while index_alt != []:
        sequence_list[index_alt[0]] = repeats_alt[0] # add target letter at beginning index
        sequence_list[index_alt[0] + n] = repeats_alt[0] # add target letter at end index
        del index_alt[0] # remove the current index so we access the proper one in the next iteration
        del repeats_alt[0] # remove the current index so we access the proper one in the next iteration
    for i in range(block_length): # fill in remaining blank spaces
        if sequence_list[i] == 0:
            # multiple cases to prevent out of bound errors
            if i >= n and not (i <= block_length - n - 1):
                while letter == sequence_list[i - n]: # check backwards, not forwards
                    letter = chr(random.choice(range(65,91)))
            elif i <= block_length - n - 1 and not (i >= n):  # check backwards, not forwards
                while letter == sequence_list[i + n]: # make sure we dont accidentally add another nback
                    letter = chr(random.choice(range(65,91)))
            else:  # check both backwards and forwards
                while letter == sequence_list[i + n] or letter == sequence_list[i - n]: # make sure we dont accidentally add another nback
                    letter = chr(random.choice(range(65,91)))
            sequence_list[i] = letter
    return index, sequence_list

# function for recording responses
def record_response(targs_identified, total_targs, false_alarms, non_targs, nback_level, d_prime_value, log):
    # record the responses
    header_list = [targs_identified, total_targs, false_alarms, non_targs, nback_level, d_prime_value]
    # convert to string
    header_str = map(str, header_list)
    # convert to a single line, separated by commas    
    header_line = ','.join(header_str)
    header_line += '\n'
    log.write(header_line)

# displays a given stimulus
def display_stimulus(letter):
    win.fill(background_col)
    draw_square()
    msg_to_screen_centered(letter, BLACK, extra_large_font)
    pg.display.flip()

# updates game, score, correct proportion and false alarm proportion
def level_change(index, responses, n, gametype, score, hit_rate, fa_rate):
    correct = 0 # correct
    fa = 0 # false alarms
    # calculate correct
    for i in range(len(index)): # look at each index and see if user clicks button n trials later
        if responses[index[i] + n] == 1:
            correct += 1
    hitrate = correct / len(index) # calculates proportion correct out of actual targets
    hit_rate.append(hitrate) 

    for i in range(len(responses)): #record number of false alarms
        if (responses[i] == 1) and not ((i - n) in index):
            fa += 1
    farate = fa / (block_length - len(index)) # calculates rate of false alarms as a proportion
    fa_rate.append(farate) 

    if gametype == "guide":
        n += 1
        return correct, fa, n, score

    performance = 0.5 * (hitrate + (1 - farate))
    if performance > 0.9: # success condition
        score += n # score increases by n
        n += 1
    elif performance < 0.5: # failure condition
        n -= 1
    else: # do nothing condition
        pass
    if n < 1:
        n = 1
    if score < 0:
        score = 0
    return correct, fa, n, score, hit_rate, fa_rate

def welcome_messages(gametype, high_score):
    if gametype == 'guide':
        guide_screen_nback("start")
        wait_key()

        # == Fixation cross screen ==
        guide_screen_nback("practice")
        wait_key()

    if gametype == 'real':
        high_score_info(high_score)

def end_messages(gametype, recorder):
    win.fill(background_col)
    if gametype == 'real':
        win.fill(background_col)
        multi_line_message(experim_fin_txt, large_font, ((win_width - (win_width / 10)), 150))
        pg.display.flip()
        wait_key()
        recorder.close()
    else:
        guide_screen_nback("finished")
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
        with open(os.path.join(highscore_path,'highscores.csv')) as f:
            i = 0
            for line in f: # grabs highscore (last line in highscore file)
                if i == 0:
                    pass
                else:
                    high_score = int(line)
                i += 1
            f.close()
    else: # if no directory exists then create one and a highscore file
        f = open(os.path.join(highscore_path,'highscores.csv'), 'w')
        f.write('High Scores\n')
        f.close()
        f = open(os.path.join(highscore_path,'highscores.csv'), 'a')
        f.write("0\n")
        f.close()

    # == Prepare a CSV file for trial data ==
    mot_log = date_sys + ' pcpnt_' + participant + ' obsvr_' + observer +'.csv'
    filename = os.path.join(results_path, mot_log)
    log = open(filename, 'w')
    header = ["targets_identified", "total_targets", "false_alarms", "total_non_targets", "n", "d-prime"]
    delim = ",".join(header)
    delim += "\n"
    log.write(delim)
    return log, highscore_path, high_score, observer, participant, date_sys

# calculate a d-prime for a trial and update the overall list
# method from https://lindeloev.net/calculating-d-in-python-and-php/
def d_prime(hit_rate, fa_rate, dprimes, total_hits):
    hits = round(hit_rate[-1] * total_hits) # calculate total hits
    misses = total_hits - hits # total misses
    false_alarms = round(fa_rate[-1] * (block_length - total_hits)) # number of false alarms
    correct_rejections = (block_length - total_hits) - false_alarms # number of correct rejections

    # values for fixing extreme d primes
    half_hit = 0.5 / (hits + misses)
    half_fa = 0.5 / (false_alarms + correct_rejections)
    # fix extreme hit rate
    hitrate = hit_rate[-1]
    if hitrate == 1:
        hitrate = 1 - half_hit
    if hitrate == 0:
        hitrate = half_hit

    # fix extreme fa rate
    farate = fa_rate[-1]
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

# runs trials (possible off by one errors.)
def trials(n, gametype, total_blocks, highscore, log, outlet):
    # initializing variables    
    # ==============================================================================================
    message_shown = False
    stim_start = False
    stim_end = False
    count = 0 
    completed_blocks = 0 
    score = 0 # initialization
    t0 = pg.time.get_ticks()
    submitted = False # keeps track of if a user submits on a given trial
    index, letters_list = generate_trial(n)
    letter = letters_list[0]
    responses = [0] * block_length # keeps track of user responses (1 = affirmative and 0 = no response)
    hit_rate = []
    fa_rate = []
    dprimes = []
    #================================================================================================
    welcome_messages(gametype, highscore) # welcome messages
    while True:
        t1 = pg.time.get_ticks()
        dt = t1 - t0 # update time
        if completed_blocks < total_blocks:
            # ========================================================
            # show screen indicating which level we are on (which n-back n we are using)
            if message_shown == False:
                n_back_screen(n) # display which task it is
                message_shown = True
                t0 = pg.time.get_ticks()
            # ========================================================
            elif count < block_length and message_shown == True:
                if dt <= stimulus_time: # displays a single stimulus
                    stim_end = False
                    if stim_start == False:
                        outlet.push_sample(['stim_start']) 
                        stim_start = True
                    for event in pg.event.get(): # key control
                        if event.type == pg.QUIT:
                            pg.quit()
                            sys.exit()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_SPACE:
                                outlet.push_sample(['space'])
                                if submitted == False:
                                    submitted = True # record key press 
                                    responses[count] = 1 # user believes it is an nback target
                            elif event.key == pg.K_q or event.key == pg.K_ESCAPE:
                                if gametype == 'real':
                                    outlet.push_sample(['esc'])
                                    return score # quit the game
                                else:
                                    return 'esc'
                            elif event.key == pg.K_k: # allows you to skip to real trials
                                if gametype == 'guide':
                                    return 'k'
                    display_stimulus(letter)
                else: # switches stimulus
                    if stim_end == False:
                        outlet.push_sample(['stim_stop'])
                        stim_end = True
                    if submitted == False:
                        responses[count] = 0 # if user does not respond, then record their nonresponse
                    submitted = False
                    stim_start = False
                    count += 1
                    blank_screen() # give blank screen before next stimulus
                    if count < block_length: # update to next letter unless this is the last letter
                        letter = letters_list[count]
                    t0 = pg.time.get_ticks() # reset time measure
            else: # reset for next block
                # =====================================
                # reseting variables
                completed_blocks += 1 
                count = 0
                submitted = False
                message_shown = False
                total = len(index) # total targets
                n_holding = n # holding variable because I messed up building functions
                # =======================================
                if gametype == 'guide':
                    correct, fa, n, score = level_change(index, responses, n, gametype, score, hit_rate, fa_rate)
                else:
                    correct, fa, n, score, hit_rate, fa_rate = level_change(index, responses, n, gametype, score, hit_rate, fa_rate) # checks users performance (only based on correct hits, but should be generalizable to false alarms)
                dprimes = d_prime(hit_rate, fa_rate, dprimes, total)
                if gametype == 'real':
                    record_response(correct, len(index), fa, block_length - len(index), n_holding, dprimes[-1], log) # will only save data from completed block!
                responses = [0] * block_length # reset responses
                index, letters_list = generate_trial(n) # generates a new set of letters and indices for targets
                letter = letters_list[count] # update letter to first letter from new set of letters
                correct_screen(n, correct, fa, total) # display how many targets the user hit
                if gametype == 'real': # display score if applicable
                    score_screen(score) # various message screens
        else: # quit game and give end message screens. 
            end_messages(gametype, log)
            if gametype == 'real':
                return score
            else:
                return 'completed'

def main(unified):
    nback_play_again = True
    while nback_play_again == True:
        now = datetime.now()
        time = now.strftime("%H:%M:%S") # get current time
        # == Initiate pygame and collect user information ==
        pg.init()
        log, highscore_path, high_score, observer, participant, date_sys = prepare_files()

        # prepare lab streaming layer functionality
        info = StreamInfo('MOT_stream', 'Markers', 1, 0, 'string', '_Obs_' + observer + '_ptcpt_' + participant + '_' + date_sys + '_' + time)
        outlet = StreamOutlet(info)

        # == Start guide/practice rounds  ==
        key = trials(1, "guide", prac_blocks, high_score, log, outlet)
        score = 0

        # == Start real trials, recording responses ==
        if key == 'k' or 'completed':
            score = trials(1, "real", real_blocks, high_score, log, outlet)
        else:
            score = 0
            
        if score > high_score: # update high score if applicable
            f = open(os.path.join(highscore_path,'highscores.csv'), 'a')
            f.writelines(str(score) + '\n')
            f.close()
            new_high_score(score)
        
        # allow user to play again without rerunning program
        nback_play_again = play_again_exp()
        if nback_play_again == True:
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