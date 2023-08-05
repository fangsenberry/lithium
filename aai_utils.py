# Import the AssemblyAI module
import assemblyai as aai
import os
import time
import requests

def transcribe(path, speaker_labels=True):
    start_time = time.time()
    # Your API token is already set here
    aai.settings.api_key = os.getenv("AAI_API_KEY")

    # Create a transcriber object.
    transcriber = aai.Transcriber()

    # If you have a local audio file, you can transcribe it using the code below.
    # Make sure to replace the filename with the path to your local audio file.
    transcript = transcriber.transcribe(path, config=aai.TranscriptionConfig(speaker_labels=speaker_labels))

    # Alternatively, if you have a URL to an audio file, you can transcribe it with the following code.
    # Uncomment the line below and replace the URL with the link to your audio file.
    # transcript = transcriber.transcribe("https://storage.googleapis.com/aai-web-samples/espn-bears.m4a")

    # After the transcription is complete, the text is printed out to the console.

    end_time = time.time()
    print(f"Transcription took {end_time - start_time} seconds")
    print(f"Transcription Confidence is: {transcript.confidence}\n")

    if speaker_labels:
        # extract all utterances from the response
        utterances = transcript.utterances
        total_transcript = ""
        # For each utterance, format it into the total transcript
        for utterance in utterances:
            speaker = utterance.speaker
            text = utterance.text
            total_transcript += f"Speaker {speaker}:\n{text}\n\n"
            # print(f"Speaker {speaker}:\n{text}\n\n")

        return total_transcript
    else:
        return transcript.text
    
def retrieve(id, speaker_labels=True):
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{id}"

    headers = {
    'authorization': os.getenv("AAI_API_KEY"),
    'content-type': 'application/json'
    }

    response = requests.get(polling_endpoint, headers=headers)
    print(response)

    #early return if something goes wrong
    if response.status_code != 200:
        return None

    #decide what to do based on speaker labels
    transcript = response.json()

    if speaker_labels:
        # extract all utterances from the response
        utterances = transcript['utterances']
        total_transcript = ""
        # For each utterance, format it into the total transcript
        for utterance in utterances:
            speaker = utterance['speaker']
            text = utterance['text']
            total_transcript += f"Speaker {speaker}:\n{text}\n\n"
            # print(f"Speaker {speaker}:\n{text}\n\n")

        return total_transcript
    else:
        return transcript['text']