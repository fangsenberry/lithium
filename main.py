import datetime

import aai_utils
import intelligence

def main():

    mode = input("(1: Transcribe, 2: Summarise, 3: Both): ")
    filename = input("filename? including suffix: ")
    path = "input/" + filename
    #some output formatting
    curr_date = datetime.date.today().strftime("%B %d, %Y")

    transcript = None
    summary = None

    #switch cases for all of them
    match mode:
        case "1":
            transcript = aai_utils.transcribe(path)
        case "2":
            with open(path, "r") as f:
                data = f.read()
            summary = intelligence.summarise(data)
        case "3":
            transcript = aai_utils.transcribe(path)
            summary = intelligence.summarise(transcript)

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