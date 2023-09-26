'''
Serves as our front end interface, using discord
'''
import discord
import os
import asyncio
import threading
import time
import sys

import json

import aai_utils
import intelligence

import datetime

from discord.ext import commands

discord_queue = asyncio.Queue()

test_mode = False

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

channel_id = 1156112759008800808

async def process_queue():
    global discord_queue
    while True:
        if not discord_queue.empty():
            title, msg, file_path, color = await discord_queue.get()
            asyncio.create_task(send_message(title, msg, file_path, color))
        else:
            await asyncio.sleep(1)  # wait for 1 second if queue is empty

async def send_message(title: str, msg: str, file_path: str = None, color=discord.Color.yellow()):
    '''
    Sends the message to the discord server with specified global channel_id.
    Discord API only allows sending of one file per message via API, so we send seperate messages.
    '''
    global bot
    global channel_id

    channel = bot.get_channel(channel_id)

    embed = discord.Embed(title=title, description=msg, color=color)

    if not file_path:
        await channel.send(embed=embed)
        return #early return

    file = discord.File(file_path)
    await channel.send(embed=embed, file=file)
    os.remove(file_path)


'''
Target function for init the thread.
'''
def lithium_helper(args: str, pathname: str = None) -> None:
    global discord_queue
    #this is a new thread, so we start out processing.
    #set some flags for parsing what we want our shit to do.

    args = args.split()
    command = args[0]
    pathname = args[1]

    if command != '!summarise':
        err_title = f"COMMAND NOT RECOGNISED ERROR"
        err_msg = f"Your command {command} was not recognised. Please try again."

    args = args[2:] #delete the first two args/command

    flags = {'-p':pathname , '--split': False, '--sum':False}

    i = 0
    while 1 < len(args):
        if args[i] == '-p':
            if pathname:
                err_title = f"ERROR WITH COMMAND"
                err_msg = f"You can't transcribe an online url and a file in the same message. Please try again."
                discord_queue.put_nowait(err_title, err_msg, None, discord.Color.red())
                break
            elif i+1 >= len(args): #no other args after this, wrong, no URL
                err_title = f"ERROR WITH COMMAND"
                err_msg = f"You have failed to provide an online url after setting -o.\n\nYou must either provide a url to transcribe from with the -o flag, or attach a file together WITH your message.\nThe file must be attached in the SAME message."
                discord_queue.put_nowait(err_title, err_msg, None, discord.Color.red())
                break
            else:
                flags['-o'] = args[i+1]
                i+=1 #skip the -o flag argument
        elif args[i] == '--split':
            flags['--split'] = True
        elif args[i] == '--sum':
            flags['--sum'] = True
        else:
            err_title = f"ERROR WITH COMMAND"
            err_msg = f"Invalid flag: {args[i]}"
            discord_queue.put_nowait(err_title, err_msg, None, discord.Color.red())
            break

    #check if they supplied an -o or not if filepath is empty
    if (len(flags['-o']) == 0):
        err_title = f"ERROR WITH COMMAND"
        err_msg = f"You have failed to provide an online url after setting -o.\n\nYou must either provide a url to transcribe from with the -o flag, or attach a file together WITH your message.\nThe file must be attached in the SAME message."
        discord_queue.put_nowait(err_title, err_msg, None, discord.Color.red())
        return #early return

    try:
        transcript = aai_utils.transcribe(flags['-o'], flags['--split'])
    except Exception as e:
        err_title = f"Encountered Error while trying to transcribe {flags['-o']}"
        err_msg = f"Error: {e}"
        discord_queue.put_nowait(err_title, err_msg, None, discord.Color.red())
        return

    #some output formatting
    filename = pathname.split(".")[0]
    curr_date = datetime.date.today().strftime("%B %d, %Y")
    transcript_path = f"temp/{filename} Transcript on {curr_date}.txt"

    #save the transcript as a file
    with open(transcript_path, "w") as f:
        f.write(transcript)

    msg_title = f"Transcript of {filename} on {curr_date}"
    msg = f"Please refer to the attached file for your transcript."

    discord_queue.put_nowait(msg_title, msg, transcript_path, discord.Color.green())

    if (flags['--sum']):
        summary = intelligence.summarise(transcript)
        #save the summary as a file
        summary_path = f"temp/{filename} Summary on {curr_date}.txt"
        with open(summary_path, "w") as f:
            f.write(summary)

        #send to discord
        msg = f"Please refer to the attached file for your summary."
        discord_queue.put_nowait(msg_title, msg, summary_path, discord.Color.green())

    #keep the audio file for now, but soon will remove.
    
#start our discord bot
def main():
    @bot.event
    async def on_ready():
        print(f"We have logged in as {bot.user}")
        bot.loop.create_task(process_queue())
        await bot.change_presence(activity=discord.Game(name="with your mind"))

    @bot.event
    async def on_message(message):
        if message.author == bot.user: #dont reply to ourselves, the bot
            return
        
        #check if the author has the appropriate permissions
        if message.author.role != "admin":
            await message.channel.send(f"Sorry, {message.author.mention}, you don't have the appropriate permissions to use this bot.")
            return

        attachments = message.attachments
        if len(attachments) > 0:
            for attachment in attachments:
                # Here we download the attachment to the filesystem
                # Note: You can change the 'attachment.filename' to any file path you want
                # it determines where and with what name the file is saved
                pathname = f"temp/{attachment.filename}"
                await attachment.save(pathname)

                threading.Thread(target=lithium_helper, args=(message.content, pathname)).start()
        else:
            threading.Thread(target=lithium_helper, args=(message.content, None)).start()

        discord_queue.put_nowait(f"Processing Task \"{message.content}\"", f"Started to process \"{message.content}\"", None, None)
    
    bot.run(os.getenv("LITHIUM_DISCORD_TOKEN"), reconnect=True)
   
if __name__ == '__main__':
    main()