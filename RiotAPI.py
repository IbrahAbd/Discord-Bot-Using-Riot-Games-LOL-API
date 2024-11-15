from typing import Final
from discord import Intents,Client,Message
from discord.ext import tasks, commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import asyncio
import os
import requests
import math
import json
import logging
import random
import discord

from ranks import *
from loadReadSave import *
from ImageGen import *
from leaderboard import *
from Mastery import *


key = '' # Add your RIOT API key here!


#---------------------------------------------------------------------------------------------------------------
# Requesting and storing data from RIOT API.
#---------------------------------------------------------------------------------------------------------------

filename = 'puuidPairs.txt'
puuidPairs = load_data_from_txt(filename)

MostRecentMatches = [None] * 16 # Will need to change this number to match amount in puuidPairs.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def APIrequest():
    for i in range(len(puuidPairs)):
        try:
            playerInfo = list(puuidPairs.values())[i]
            matchesURL = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{playerInfo[2]}/ids?start=0&count=5&api_key={key}'
            matchResponse = requests.get(matchesURL)
            matchResponse.raise_for_status()  # Raise an exception for HTTP errors
            match = matchResponse.json()
            if not match:
                logging.warning(f"No matches found for player {playerInfo[0]}!")
                continue
            
            mostRecentGameName = match[0]
            
            if MostRecentMatches[i] == mostRecentGameName:
                logging.info(f"No new game played for {playerInfo[0]}!")
                continue
            elif playerInfo[6] == mostRecentGameName:
                logging.info(f"Skipping previous game for {playerInfo[0]}\n")
                continue
            else:
                MostRecentMatches[i] = mostRecentGameName
                matchDataURL = f"https://europe.api.riotgames.com/lol/match/v5/matches/{mostRecentGameName}?api_key={key}"
                matchDataResponse = requests.get(matchDataURL)
                matchDataResponse.raise_for_status()
                match_data = matchDataResponse.json()
                
                if match_data['info']['gameMode'] != 'CLASSIC': #Only Summoner's rift is used for the data collection.
                    logging.info(f"Skipping non-Summoner's Rift game for {playerInfo[0]}\n")
                    continue         
                
                player_data = next((participant for participant in match_data['info']['participants'] if participant['puuid'] == playerInfo[2]), None)
                if player_data is None:
                    logging.warning(f"No player data found for {playerInfo[0]} in match {mostRecentGameName}!")
                    continue
                
                kp = next((participant['challenges']['killParticipation'] for participant in match_data['info']['participants'] if 'challenges' in participant and 'killParticipation' in participant['challenges'] and participant['challenges']['killParticipation'] > 0), None)
                
                champ = player_data['championName']
                k = player_data['kills']
                d = player_data['deaths']
                a = player_data['assists']
                win = player_data['win']
                penta = player_data['pentaKills']
                quadra = player_data['quadraKills']
                triple = player_data['tripleKills']
                win = player_data['win']
                cs = player_data['totalMinionsKilled']
                csJungle = player_data['neutralMinionsKilled']
                csTotal = cs+csJungle
                game_duration_seconds = match_data['info']['gameDuration']
                csPerMin = round((csTotal/(game_duration_seconds/60)),1)
                
                if d == 0:  # Prevent dividing by 0 error.
                    kda = round((k + a), 1)
                else:
                    kda = round(((k + a) / d), 1)
                
                if kp is not None:
                    kp = round(kp, 1)
                
                keys_list = list(puuidPairs.keys())
                
                if (goodFinder(k, d, a, kda, kp) != ""):
                    string = goodFinder(k, d, a, kda, kp) 
                    if penta >= 1:
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"pentaKills",win,csPerMin)
                    elif quadra >= 1:
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"quadraKills",win,csPerMin)
                    elif triple >= 1:
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"tripleKills",win,csPerMin)
                    else:    
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"",win,csPerMin)
                    await channelSend(keys_list[i])
                    
                elif badFinder(k, d, a, kda, kp) == "":
                    string = badFinder(k,d,a,kda,kp) 
                    if string != "":
                        if penta >= 1:
                            generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,False,"pentaKills",win,csPerMin)
                        elif quadra >= 1:
                            generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,False,"quadraKills",win,csPerMin)
                        elif triple >= 1:
                            generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,False,"tripleKills",win,csPerMin)
                        else:    
                            generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,False,"",win,csPerMin)                        
                        await channelSend(keys_list[i])
                    
                update_player_data(playerInfo[0], k, d, a, MostRecentMatches[i])
                logging.info(f"Processed player {playerInfo[0]} - Match {mostRecentGameName}\n")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for player {playerInfo[0]}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error for player {playerInfo[0]}: {e}")



#--------------------------------------------------------------------------------------------------------------- 

load_dotenv()
TOKEN: Final[str] = os.getenv('TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)
        
async def send_message(message : Message, user_message:str) -> None:
    if not user_message:
        print("Message was empty because intents were not enable properly.")
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
        
    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
    
def get_response(user_input: str) -> str:
    if user_input.strip().lower() == "#kills":
        leaderboard = create_leaderboard(puuidPairs, "Kills")
        return display_leaderboard(leaderboard, "Kills")
    elif user_input.strip().lower() == "#assists":
        leaderboard = create_leaderboard(puuidPairs, "Assists")
        return display_leaderboard(leaderboard, "Assists")
    elif user_input.strip().lower() == "#deaths":
        leaderboard = create_leaderboard(puuidPairs,"Deaths")
        return display_leaderboard(leaderboard, "Deaths")
    elif user_input.strip().lower().startswith("#mastery"):
        output = ""
        parts = user_input.strip().split()
        if len(parts) >= 3 and parts[0].lower() == "#mastery":
            player_name = " ".join(parts[1:-1])
            count = int(parts[-1])
            for name, info in puuidPairs.items():
                if info[0] == player_name:
                    name = info[0]
                    puuid = info[2]
                    output = print_top_masteries(name, puuid, count)
                    break

            else:
                print("Invalid command format. Please use '#mastery PlayerName Count'.")
        return output
   
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    if user_message.startswith("#kills"):
        response = get_response(user_message)
        await message.channel.send(response)
    if user_message.startswith("#assists"):
        response = get_response(user_message)
        await message.channel.send(response)
    if user_message.startswith("#deaths"):
        response = get_response(user_message)
        await message.channel.send(response)
    if user_message.startswith("#mastery"):
        response = get_response(user_message)
        await message.channel.send(response)
        
    else:
        # Handle other messages if needed
        pass
    
    print(f'[{channel}] {username}: "{user_message}"')
    
#----------------------------------------------------------------------------

@tasks.loop(minutes=15)
async def api_request_task():
    channel = client.get_channel(0) # Put your dicord channel number here inside the ()!!
    await APIrequest()  
    print("Sending API response to channel if possible:\n")

async def send_image(channel, image_path):
    # Open the image file
    with open(image_path, 'rb') as f:
        picture = discord.File(f)
    # Send the image to the channel
    await channel.send(file=picture)
    os.remove(image_path)

async def channelSend(name:str):
    channel_id = 0 # Put your dicord channel number here!!
    channel = client.get_channel(channel_id)
    if channel:
        image_path = f'{name}.jpg' # Replace with the path to your image
        await send_image(channel, image_path)
        
@client.event
async def on_ready():
    print(f'{client.user} is now running!')
    api_request_task.start()

async def main():
    await client.start(TOKEN)
    
asyncio.run(main())