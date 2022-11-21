Update Notes (11/21/22): 
Hello, this is the updated version of the multiple object tracking paradigm code. Since we last met, I have added various different functionalities. I have not cleaned it up entirely (clean code + proper commenting + bug testing) as I have been focusing on getting the main features up and running. I will go back afterwards and work on all of this so that anyone can come and edit the code to their liking. You may need to download some packages (I do not think I am using any new ones, but I cannot be sure). In this case go to your terminal and enter 'pip install your_package' where 'your_package' is the name of the missing package.

Added Functionalities/Important comments/Edits:
1) Now the game has a three tier structure: targets, distractors, and speeds. The player first progresses through a fixed number of targets and distractors with the speed changing every time they succeed. Once they reach a predetermined maximum speed, the number of distractors will increase. They then go through all of the speeds again until they reach the maximum speed again and then another distractor is added. The number of distractors will increase until they reach the maximum number of distractors and then the number of targets will increase. I have built this code so that the maximum number of distractors and speeds is easy to change (just change the values in att_max at the top of the "MOT_exp_main.py file). The first entry is the maximum number of distractors and the second is the maximum number of speeds. I have also built this so that it will be easy to add new features to progress through if we want to add feaures beyond targets, distractors and speeds. Editing this is not as simple as just changing some numbers, but I would be happy to walk anyone through the code if they wish.

2) There is now a white box in the bottom right corner that flashes when the targets are flashing and disappears when the trials begin. This is for our photosensor. Let me know if there is another time period where you all want to have that box flashing. I have not yet added the functionality for lab streaming layer. That will come later as I need to figure out how lsl works on windows but need to tend to some class work for the next couple of days. 

3) I have added a feature for introducing a break for the users. Currently I have a naive approach for it (after progressing 5 stages they get a break) but I made it so that it will be very easy to change. It is more of a proof of concept. 

4) IMPORTANT: I modified where the information from each trial is stored. You will need to change the "save_path" variable within the "MOT_constants.py" file because it is currently designed for my my computer/file paths and my testing purposes. If you dont want to deal with all of that hooplah, then I reccomend changing the "filepath" variable under the "main" function within "MOT_exp_main.py" file from "filename = save_path + mot_log +'.csv'" to "filename = mot_log +'.csv'" and I believe that it will still work. 

5) I have made the code shorter by removing the functions for guide trials and practice trials. It was basically the same, very long bit of code 3 times in a row. So now it all falls under the "trials" function. 

6) All of these features currently work on my device. But if you run into any trouble at all, please reach out to me at dtfalk@uchicago.edu or send me a text at 413-884-2553. I am very happy to help get the program running or walk anyone through how the code works. 

# multiple-object-tracking-paradigm

This is the multiple object tracking paradigm, as first described by Pylyshyn and Storm (1988). In this very experiment, the objects follow a Brownian motion and expected to indicate all the objects they have been tracking instead of selecting if one object has been tracked or not.

Note that this multiple object tracking is ***NOT RELATED TO COMPUTER VISION***.

Change n_prac and n_real variables in the main file to change how many practice and real trials there will be, respectively.

Dependencies: PyGame, PsychoPy

To run the MOT experiment, download and run the main experiment file; requires MOT_constants.py and messagescreens.py to run. The GUIDED experiment file includes a step-by-step guide.
