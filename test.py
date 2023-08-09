'''
For retrieving things that have broken halfway.
'''
import aai_utils as aai
import os
import intelligence as int

header = {
    'authorization': os.getenv("AAI_API_KEY"),
    'content-type': 'application/json'
}

transcript_id = "67svsjtpb1-61c4-446a-9aa6-b18f5a8eb2fe"

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

poll = transcript_endpoint + "/" + transcript_id

transcript = aai.get_transcript(poll, header)

print(transcript)

print("here")

total = ""
with open("transcript.txt", "w") as f:
    for utter in transcript['utterances']:
        total += utter['text'] + "\n"
        f.write(utter['speaker'] + ": \n\n")
        f.write(utter['text'] + "\n\n")

summary = int.summarise(total)

with open("summary.txt", "w") as f:
    f.write(summary)

print("done")