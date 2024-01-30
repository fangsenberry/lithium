import sys
from pathlib import Path

# Path to the directory containing yggdrasil
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir))

# Now you can import from yggdrasil
from yggdrasil import midgard, ratatoskr

import threading
import concurrent

from tqdm.auto import tqdm

class Lithium():
    def __init__(self) -> None:
        self.system_init = f"You are an genius AI that works with content."
    
    def clean_transcript(self, transcript):
        print(f"num tokens of transcript: {midgard.get_num_tokens(transcript)}")
        sentences = transcript.split('.')
        
        #formulate the chunks
        chunks = []
        curr_chunk = ""
        
        for sentence in sentences:
            if midgard.get_num_tokens(curr_chunk) > 512:
                # print(f"length of chunk {len(chunks)}: {midgard.get_num_tokens(curr_chunk)}")
                chunks.append(curr_chunk)
                curr_chunk = ""
            
            curr_chunk += sentence
            
        #handle the last case
        chunks.append(curr_chunk)
        cleaned = ""
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Create a dictionary to store futures and their corresponding indices
            future_to_index = {}
            results = [None] * len(chunks)  # Create a list to store results in order

            # Submit tasks and store future with index
            for index, chunk in enumerate(chunks):
                future = executor.submit(self.clean_transcript_helper, chunk)
                future_to_index[future] = index

            # As futures complete, place the result in the correct index
            for future in tqdm(concurrent.futures.as_completed(future_to_index), total=len(chunks), desc="Cleaning chunks"):
                index = future_to_index[future]
                results[index] = future.result()

        # Combine the results in order
        cleaned = ''.join(results)
        return cleaned

        
        
    def clean_transcript_helper(self, sentence):
        prompt = f"""I am going to give you a chunk from a transcript. There might be grammatical or other errors in the chunk. Please correct the chunk while preserving all of the original detail and nuance. To be clear, you can reconstruct the sentences within the chunk so that it is grammatically correct, but you cannot change the meaning of the sentence or the information presented, and the chunk should be largely preserved, albeit all the errors fixed. You should also insert appropriate paragraphing when you find it appropriate. You MUST only return the raw text of the requested response. I am algorithmically checking your response, so please do not include any additional information, because this will cause the algorithm to break.
        
        Here is the sentence:
        {sentence}"""
        
        return midgard.call_gpt_single(self.system_init, prompt, function_name="clean_transcript_helper", to_print=False)