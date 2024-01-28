import datetime
import os
import sys
from pathlib import Path

import aai_utils
import intelligence

# Path to the directory containing yggdrasil
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir))

# Now you can import from yggdrasil
from yggdrasil import midgard, ratatoskr

def main():
    mode = input("(1: Transcribe, 2: Summarise, 3: Both): ")
    url = None
    #check if 1 or 3 and ask if they want to take an online url
    if mode == "1" or mode == "3":
        url = input("Do you want to take an online url? (y/n): ")
        if url == "y":
            path = input("Enter the url: ")
            filename = "Online URL"
    
    if url == None or url != "y":
        paths = os.listdir("input/")

        print("--------------------")
        for i, path in enumerate(paths):
            if (path == ".DS_Store"): continue
            print("num: ", i, "| filename: ", path)
        print("--------------------\n")

        path_choice = input("Enter the number of the file you want to analyse: ")
        path = "input/" + paths[int(path_choice)]
        filename = paths[int(path_choice)].split(".")[0]

    #some output formatting
    curr_date = datetime.date.today().strftime("%B %d, %Y")

    #check if they want us to split speakers
    if mode == "1" or mode == "3":
        speaker_labels = input("Do you want to split speakers? (y/n): ")
        speaker_labels = (speaker_labels == 'y')

    #rat instance
    rat = ratatoskr.Ratatoskr()

    is_chinese = input("Is the language Chinese? (y/n): ") == 'y'

    transcript = None
    summary = None

    #switch cases for all of them
    match mode:
        case "1":
            transcript = rat.speech_to_text(path, speaker_labels, is_chinese)
        case "2":
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
                data = data.replace("\ufffd", " ")
            summary = midgard.summarise(data)
        case "3":
            transcript = rat.speech_to_text(path, speaker_labels, is_chinese)
            summary = midgard.summarise(transcript)

    if transcript is not None:
        path = "output/" + filename + " Transcript " + curr_date + ".txt"
        with open(path, "w") as f:
            f.write(transcript)
    
    if summary is not None:
        path = "output/" + filename + " Summary " + curr_date + ".txt"
        with open(path, "w") as f:
            f.write(summary)

    return

if __name__ == '__main__':
    main()