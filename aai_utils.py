import requests
import time
import os

import grammarfix

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

def transcribe(audio_path, split_speakers=True):
    start = time.time()

    api_key = os.getenv("AAI_API_KEY")
    if api_key is None:
        raise RuntimeError("AAI_API_KEY environment variable not set. Try setting it now..")
    
    # Create header with authorization along with content-type
    header = {
        'authorization': api_key,
        'content-type': 'application/json'
    }

    # Upload the audio file to AssemblyAI
    print("Uploading file to AssemblyAI servers...")
    upload_url = upload_file(audio_path, header)
    print("File uploaded to AssemblyAI servers.")\
    
    # Request a transcription
    print("Requesting transcript from AssemblyAI")
    transcript_response = request_transcript(upload_url, header, split_speakers)

    # Create a polling endpoint that will let us check when the transcription is complete
    polling_endpoint = make_polling_endpoint(transcript_response)

    # Wait until the transcription is complete
    wait_for_completion(polling_endpoint, header)
    print("Transcription Done.")
    # Request the paragraphs of the transcript
    # paragraphs = aai_utils.get_paragraphs(polling_endpoint, header)

    #request the transcript
    print("Getting Transcript...")
    transcript = get_transcript(polling_endpoint, header)
    print("Transcript Confidence: ", transcript['confidence'])
    print("Got Transcript.")
    # Save and print transcript
    # with open('transcript.txt', 'w') as f:
    #     for para in paragraphs:
    #         print(para['text'] + '\n')
    #         f.write(para['text'] + '\n')

    print("Time taken: ", (time.time() - start)/60, " minutes")

    print("Fixing Grammar...")

    complete_fixed = ""
    utterances = transcript['utterances']
    for utterance in utterances:
        #split the utterance into chunks of 50000 characters
        if (len(utterance['text']) > 50000):
            #split the utterance into chunks of 50000 characters
            chunks = [utterance['text'][i:i+50000] for i in range(0, len(utterance), 50000)]
            for chunk in chunks:
                fixed = grammarfix.fix_grammar(chunk)
                complete_fixed += utterance['speaker']
                complete_fixed += "\n\n------------------------------------\n\n"
                complete_fixed += fixed
        else:
            fixed = grammarfix.fix_grammar(utterance['text'])
            complete_fixed += utterance['speaker']
            complete_fixed += fixed

    print("Grammar Fixed.")

    return complete_fixed #returning a string


# Helper for `upload_file()`
def _read_file(filename, chunk_size=5242880):
    with open(filename, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


# Uploads a file to AAI servers
def upload_file(audio_file, header):
    upload_response = requests.post(
        upload_endpoint,
        headers=header, data=_read_file(audio_file)
    )
    return upload_response.json()


# Request transcript for file uploaded to AAI servers
def request_transcript(upload_url, header, 
split_speakers, topic_detection=False, summarize=False, split_chapters=False):
    
    if (split_chapters):
        summarize = False #this is because auto chapters also gies a summary for each chapter.

    transcript_request = {
        'audio_url': upload_url['upload_url'],
        'iab_categories': topic_detection,

        'speaker_labels': split_speakers,

        'auto_chapters': split_chapters,

        'summarization': summarize,
        'summary_model': 'informative',
        'summary_type': 'bullets'

    }
    transcript_response = requests.post(
        transcript_endpoint,
        json=transcript_request,
        headers=header
    )
    return transcript_response.json()


# Make a polling endpoint
def make_polling_endpoint(transcript_response):
    polling_endpoint = "https://api.assemblyai.com/v2/transcript/"
    polling_endpoint += transcript_response['id']
    return polling_endpoint


# Wait for the transcript to finish
def wait_for_completion(polling_endpoint, header):
    while True:
        polling_response = requests.get(polling_endpoint, headers=header)
        polling_response = polling_response.json()

        if polling_response['status'] == 'completed':
            break

        time.sleep(5)


# Get the paragraphs of the transcript
def get_paragraphs(polling_endpoint, header):
    paragraphs_response = requests.get(polling_endpoint + "/paragraphs", headers=header)
    paragraphs_response = paragraphs_response.json()

    paragraphs = []
    for para in paragraphs_response['paragraphs']:
        paragraphs.append(para)

    return paragraphs

def get_transcript(polling_endpoint, header):
    transcript_response = requests.get(polling_endpoint, headers=header)
    transcript_response = transcript_response.json()

    return transcript_response #this is the "confidence the model has in the transcribed text"