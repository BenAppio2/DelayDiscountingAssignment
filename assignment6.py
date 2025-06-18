import pandas as pd
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim, Rect, TextBox
from psychopy.core import Clock, quit, wait
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard
from psychopy import event
import random
### DIALOG BOX ROUTINE ###
exp_info = {'participant_nr': '', 'age': '','condition':['future','past']}
dlg = DlgFromDict(exp_info)

# If pressed Cancel, abort!
if not dlg.OK:
    quit()

# Initialize a fullscreen window with my monitor (HD format) size
# and my monitor specification called "samsung" from the monitor center
win = Window(size=(1200, 800), fullscr=False, monitor='samsung')

# Also initialize a mouse, although we're not going to use it
mouse = Mouse(visible=True)

# Initialize a (global) clock
clock = Clock()

# Initialize Keyboard
kb = Keyboard()
kb.clearEvents()

### WELCOME ROUTINE ###
# Create a welcome screen and show for 2 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", color=(1, 0, -1), font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(2)

### INSTRUCTION ROUTINE ###
instruct_txt = """ 
In this task, you will choose between $20 today or a larger amount after a delay.

Some trials will include a future event (e.g., Graduation).

Click on your preferred option to choose.

Press 'q' at any time to quit the experiment.

(Press ‘enter’ to start the experiment!)
"""
 
# Show instructions and wait until response (return)
instruct_txt = TextStim(win, instruct_txt, alignText='left', height=0.085)
instruct_txt.draw()
win.flip()

# Initialize keyboard and wait for response
kb = Keyboard()
while True:
    keys = kb.getKeys()
    if 'return' in keys:
        # The for loop was optional
        for key in keys:
            print(f"The {key.name} key was pressed within {key.rt:.3f} seconds for a total of {key.duration:.3f} seconds.")
        break  # break out of the loop!

cue_list = 'cue_trials.csv'

offer_trial = pd.read_csv(cue_list)
offer_trial = offer_trial.sample(frac=1)

# Create fixation target (a plus sign)
fix_target = TextStim(win, '+')
trial_clock = Clock()

# START exp clock
clock.reset()

# Show initial fixation
fix_target.draw()
win.flip()
wait(1)

rec1= Rect(win=win, size=0.4, fillColor=[0, 1, 0], lineColor=[1, 0, 0],pos=(-0.5,0)) 
rec2 = Rect(win=win, size=0.4, fillColor=[0, 1, 0], lineColor=[1, 0, 0],pos=(0.5,0)) 
rec_select1= Rect(win=win, size=0.6, fillColor=None, lineColor=[1, 0, 0],lineWidth=10, pos=(-0.5,0)) 
rec_select2 = Rect(win=win, size=0.6, fillColor=None, lineColor=[1, 0, 0],lineWidth=10, pos=(0.5,0))

# Add columns to store responses
offer_trial['resp'] = ""
offer_trial['rt'] = ""
offer_trial['onset'] = -1

# Track how many delayed choices were made in each condition
delayed_counts = {'cue': 0, 'no_cue': 0}

# Start the trial loop
for idx, row in offer_trial.iterrows():
    # Create offer text
    im_txt = "$20 today"
    del_txt = str(row['delayed_amount']) + " in " + str(row['delay'])  + " days"

    # Randomize left/right side
    n = random.randint(0, 1)
    if n == 0:
        stim_txt1 = TextStim(win, im_txt, pos=(0.5, 0))
        stim_txt2 = TextStim(win, del_txt, pos=(-0.5, 0))
        rec1.pos = (0.5, 0)
        rec2.pos = (-0.5, 0)
        rect1_type = "immediate"
        rect2_type = "delayed"
    else:
        stim_txt1 = TextStim(win, im_txt, pos=(-0.5, 0))
        stim_txt2 = TextStim(win, del_txt, pos=(0.5, 0))
        rec1.pos = (-0.5, 0)
        rec2.pos = (0.5, 0)
        rect1_type = "immediate"
        rect2_type = "delayed"

    # Cue text (if present)
    cue_txt = None
    if pd.notna(row['cue']) and row['cue'].strip() != "":
        cue_txt = TextStim(win, text=row['cue'], pos=(0, 0.5))


    # Trial start
    trial_clock.reset()
    click = 0
    rt = "miss"
    resp = "miss"
    while trial_clock.getTime() < 4:
        rec1.draw()
        rec2.draw()
        stim_txt1.draw()
        stim_txt2.draw()
        if cue_txt:
            cue_txt.draw()
        win.flip()
        
        keys = kb.getKeys()
        if 'q' in keys:
            win.close()
            quit()

        if mouse.isPressedIn(rec1) and click == 0:
            rt = trial_clock.getTime()
            resp = rect1_type
            click = 1
            stim_txt1.draw()
            stim_txt2.draw()
            if cue_txt:
                cue_txt.draw()
            win.flip()
            wait(0.3)
        elif mouse.isPressedIn(rec2) and click == 0:
            rt = trial_clock.getTime()
            resp = rect2_type
            click = 1
            stim_txt1.draw()
            stim_txt2.draw()
            if cue_txt:
                cue_txt.draw()
            win.flip()
            wait(0.3)

    # Log response
    offer_trial.loc[idx, 'resp'] = resp
    offer_trial.loc[idx, 'rt'] = rt
    if offer_trial.loc[idx, 'onset'] == -1:
        offer_trial.loc[idx, 'onset'] = clock.getTime()

    if resp == "delayed":
        if row['cue'] != "":
            delayed_counts['cue'] += 1
        else:
            delayed_counts['no_cue'] += 1

    # Fixation between trials
    fix_target.draw()
    win.flip()
    wait(1)

# End of experiment: print results
print("Delayed choices with cue:", delayed_counts['cue'])
print("Delayed choices without cue:", delayed_counts['no_cue'])

# Optional: close window
win.close()
