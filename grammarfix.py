from sapling import SaplingClient
import os

'''
Function to fix generally fix grammar in any piece of text and return the fixed text
Code for applying the edits taken from https://sapling.ai/docs/api/applying-edits
'''
def fix_grammar(text, session_name="Not Set"):

    API_KEY = os.getenv("SAPLING_API_KEY")
    sapling = SaplingClient(api_key=API_KEY)
    edits = sapling.edits(text, session_name)

    edits = sorted(edits, key=lambda e: -1 * (e['sentence_start'] + e['start']))
    for edit in edits:
        start = edit['sentence_start'] + edit['start']
        end = edit['sentence_start'] + edit['end']
        if start > len(text) or end > len(text):
            print(f'Edit start:{start}/end:{end} outside of bounds of text:{text}')
            continue
        text = text[: start] + edit['replacement'] + text[end:]

    return text