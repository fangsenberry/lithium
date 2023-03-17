'''
Some basic text intelligence functions

1. Summarization
2. Key Insights
'''

import openai
import tiktoken
import os

chosen_model = "gpt-4"
print("Using model: ", chosen_model)

def get_num_tokens(input, model="text-davinci-003"):

    encoding = tiktoken.encoding_for_model(model)
    comp_length = len(encoding.encode(input)) #lower bound threshold since it seems that tiktoken is not that accurate

    return comp_length

def summarise(input):

    total_summary = ""

    sentences = input.split(".")

    num_tokens = 0
    curr_corpus = ""

    count = 0

    #the below alg essentially summarises in "chunks" of 3500 tokens so the context window does not exceed the model's limit
    for sentence in sentences:
        sentence += "." #reappend the period
        curr_corpus += sentence
        num_tokens += get_num_tokens(sentence)

        if num_tokens > 3500:
            print("count: ", count, "total number of sentence: ", len(sentences))
            #summarise
            part = summarise_helper(curr_corpus)

            total_summary += part
            curr_corpus = ""
            num_tokens = 0

        count += 1

    #account for the last iteration
    if num_tokens > 0:
        part = summarise_helper(curr_corpus)
        total_summary += part

    return total_summary

def summarise_helper(input):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    start_prompt = "You are SummarizerGPT. You create summaries that keep all the information from the original text. You must keep all numbers and statistics from the original text. You will provide the summary in succint bullet points. For longer inputs, summarise the text into more bullet points. You will be given a information, and you will give me a bulleted point summary of that information."
    
    ask_prompt = """Summarise the following text for me into a list of bulleted points.
    
    Information:
    
    {information}""".format(information=input)

    ask_prompt = start_prompt + "\n" + ask_prompt

    response = openai.ChatCompletion.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": start_prompt},
            {"role": "user", "content": ask_prompt}
        ]
    )

    return response.choices[0].message.content