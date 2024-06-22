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

'''
Everything below here is the GomInator code.
Every hour run this script.
Check each players most recent match and KDAs.
If below certain KDAs classify as assigned title.

'''

key = '' # Add your RIOT API key here!

#---------------------------------------------------------------------------------------------------------------

def goodFinder(k,d,a,kda,kp): 
    output = ""
    if (k >= 20 and d == 0):
        output += 'Incarnation'
    elif (k >= 14 and k <= 19 and d == 0):
        output +=  'Apotheosis'
    elif (k >= 8 and k <= 13 and d == 0):
        output += 'Deluxe'
    elif (k >= 5 and k <= 7 and d == 0):
        output += 'Introduction'
    elif (k == 0 and d == 0 and a >= 20):
        output += 'Ascension'
    else:
        if (k >= 10 and k <= 19 and kda >= 5):
            output += "Supreme "
        elif (k >= 20 and kda >= 5):
            output += "Ultimate "
            
        if (kda >= 5 and kda <= 9 ): 
            output +=  "Original"
        elif (kda >= 10 and kda <= 19):
            output +=  "Classic"
        elif (kda >= 20):
            output +=  "Certified Classic"
            
    return output
            
def badFinder(k,d,a,kda,kp):
    if kp == 0 and d >= 20:
        return "HOLY its a Incarnation"
    elif kp == 0 and d >= 14:
        return "An Apotheosis"
    elif kp == 0 and d >= 8:
        return "A good old Deluxe"
    elif (kp == 0 and d == 5) or (kp == 1 and d == 6):
        return "An Introduction"
    
    else:
        if d >= 20:
            if kda <= 0.2:
                return "Ultimate Certified Classic"
            elif kda <= 0.5:
                return "Ultimate Classic"
            elif kda <= 1:
                return "Ultimate Original "
            else:
                return "No official classification"

        elif d >= 14:
            if kda <= 0.2:
                return "Supreme Certified Classic"
            elif kda <= 0.5:
                return "( ͡° ͜ʖ ͡°), Supreme Classic"
            elif kda <= 1:
                return "Supreme Original"
            else:
                return "" 
        else:
            if kda <= 0.2 and kda >= 0:
                return "Certified Classic"
            elif kda <= 0.5:
                return "The one and only Classic"
            elif kda < 1:
                return "The Original"
            else:
                return "" 
                
#---------------------------------------------------------------------------------------------------------------
# Loading, reading and saving data.
#---------------------------------------------------------------------------------------------------------------
# Load data from text file
def load_data_from_txt(filename):
    data = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                name, values = line.split(":", 1)
                name = name.strip().strip('"')
                values = values.strip().strip('()').replace('"', '').split(',')
                riot_id, tagline, puuid, kills, deaths, assists, match = values[:7]
                kills = int(kills.strip())
                deaths = int(deaths.strip())
                assists = int(assists.strip())
                match = match.strip()
                data[name] = (riot_id.strip(), tagline.strip(), puuid.strip(), kills, deaths, assists, match)
    return data

# Save data to text file
def save_data_to_txt(data, filename):
    with open(filename, 'w') as file:
        for name, info in data.items():
            riot_id, tagline, puuid, kills, deaths, assists, match = info
            file.write(f'"{name}":("{riot_id}","{tagline}","{puuid}",{kills},{deaths},{assists},"{match}")\n')
            
#Update player data after every subsequent match.
def update_player_data(riot_id, kills, deaths, assists, match):
    found = False
    for name, info in puuidPairs.items():
        if info[0] == riot_id:
            player_info = list(info)
            print(f"Updating {riot_id} before: {player_info}")  
            player_info[3] += kills
            player_info[4] += deaths
            player_info[5] += assists
            player_info[6] = match
            puuidPairs[name] = tuple(player_info)
            print(f"Updating {riot_id} after: {player_info}")  
            found = True
            break
    if found:
        save_data_to_txt(puuidPairs, filename)
        print(f"Data for {riot_id} saved to {filename}")  
    else:
        print(f"{riot_id} not found in puuidPairs")                                 # Debug statement for missing player


#---------------------------------------------------------------------------------------------------------------
#Leaderboard Methods
#---------------------------------------------------------------------------------------------------------------
def create_leaderboard(puuidPairs,stat):
    leaderboard = []
    
    for player_name, player_info in puuidPairs.items():
        if stat == "Kills":
            stats = player_info[3]
        elif stat == "Assists":
            stats = player_info[5]
        elif stat == "Deaths":
            stats = player_info[4]  
            
        leaderboard.append((player_name, stats))
    
    # Sort the leaderboard based on kills in descending order
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    
    return leaderboard

def display_leaderboard(leaderboard, typeStat):
    output = ""
    if typeStat == "Kills":
        output += f"{typeStat} :x: Leaderboard:\n"
    elif typeStat == "Deaths":
        output += f"{typeStat} :skull: Leaderboard:\n"
    elif typeStat == "Assists":
        output += f"{typeStat} :handshake: Leaderboard:\n"
    
    output += "=================\n"
    for rank, (player_name, stat) in enumerate(leaderboard, start=1):
        if rank == 1:
            output += f":first_place: {player_name}: {stat}\n"
        elif rank == 2:
            output += f":second_place: {player_name}: {stat}\n"
        elif rank == 3:
            output += f":third_place: {player_name}: {stat}\n"        
        else:    
            output += f"{rank}.) {player_name}: {stat}\n"
    output += "=================\n"
    return output

#---------------------------------------------------------------------------------------------------------------
# Get Champion mastery and output the result to the dicord channel.
#---------------------------------------------------------------------------------------------------------------

champion_json = {}

def get_top_masteries_by_puuid(puuid, count):
    url =  f'https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count={count}&api_key={key}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()[:count]

def get_champion_name(champion_id):
    global champion_json

    if not champion_json:
        champion_json = get_latest_ddragon()

    for champion_name, champion_data in champion_json.items():
        if champion_data["key"] == str(champion_id):
            return champion_name
    return None

def get_latest_ddragon():
    global champion_json

    if champion_json:
        return champion_json

    versions_response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    versions_response.raise_for_status()
    latest = versions_response.json()[0]

    ddragon_response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion.json")
    ddragon_response.raise_for_status()
    champions = ddragon_response.json()["data"]
    champion_json = champions
    return champions

def print_top_masteries(name, puuid, count):
    count2 = 0
    output = ""
    try:
        top_masteries = get_top_masteries_by_puuid(puuid, count)
        output += f"Top {count} champion masteries for {name}:\n\n"
        for mastery in top_masteries:
            count2 += 1
            champion_name = get_champion_name(mastery['championId'])
            output += f"{count2}.) {champion_name}, Mastery Level: {mastery['championLevel']}, Mastery Points: {mastery['championPoints']}\n\n"
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
    return output 


#---------------------------------------------------------------------------------------------------------------
# Image generation.
#---------------------------------------------------------------------------------------------------------------
def create_circular_mask(size):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    return mask

def add_text_to_image(image, texts, text_color='black', outline_color='black', font_path=None, font_size=36, text_x=None, text_y=None, line_spacing=10, vertical=False):
    draw = ImageDraw.Draw(image)
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()

    if text_x is None:
        text_x = 10
    if text_y is None:
        text_y = 200

    y_offset = 0

    if isinstance(texts, str):
        texts = [texts]

    for text in texts:
        if vertical:
            for char in text:
                if outline_color:
                    # Draw the outline
                    draw.text((text_x - 1, text_y + y_offset - 1), char, font=font, fill=outline_color)
                    draw.text((text_x + 1, text_y + y_offset - 1), char, font=font, fill=outline_color)
                    draw.text((text_x - 1, text_y + y_offset + 1), char, font=font, fill=outline_color)
                    draw.text((text_x + 1, text_y + y_offset + 1), char, font=font, fill=outline_color)

                draw.text((text_x, text_y + y_offset), char, fill=text_color, font=font)
                y_offset += draw.textbbox((0, 0), char, font=font)[3] + line_spacing  # Move down by the height of the current text plus the line spacing
        else:
            if outline_color:
                # Draw the outline
                draw.text((text_x - 1, text_y + y_offset - 1), text, font=font, fill=outline_color)
                draw.text((text_x + 1, text_y + y_offset - 1), text, font=font, fill=outline_color)
                draw.text((text_x - 1, text_y + y_offset + 1), text, font=font, fill=outline_color)
                draw.text((text_x + 1, text_y + y_offset + 1), text, font=font, fill=outline_color)

            draw.text((text_x, text_y + y_offset), text, fill=text_color, font=font)
            y_offset += draw.textbbox((0, 0), text, font=font)[3] + line_spacing  # Move down by the height of the current text plus the line spacing

def select_random_image(character_name, directory):
    files = os.listdir(directory)

    # Filter files that match the format name_x.jpeg
    matching_files = [file for file in files if file.startswith(character_name + '_') and file.endswith('.jpg')]

    # Randomly select one of the matching files
    if matching_files:
        random_image = random.choice(matching_files)
        return os.path.join(directory, random_image)
    else:
        return None

def generateImage(characterName, personName, gamerTag, msg,k,d,a,kda,gom,multikill,win,csPerMin):
    
    directory = 'splash/'
    random_image_path = select_random_image(characterName, directory)
    background = ""
    if random_image_path:
        print(f"Selected: {random_image_path}")
        background_image = Image.open(random_image_path)
        background =  background_image
    else:
        print("No images found for the character.")
        
    output_image_path = f'{personName}.jpg'

    # Create circular mask and put profile picture into it. Reposition afterwards.
    overlay_image = Image.open(f'pfp/{personName}.png')
    circle_diameter = 175
    overlay_image = overlay_image.resize((circle_diameter, circle_diameter))
    circular_mask = create_circular_mask((circle_diameter, circle_diameter))
    overlay_image.putalpha(circular_mask)
    overlay_position = (10, 10)  # Adjust as needed
    background.paste(overlay_image, overlay_position, overlay_image)  
    
    texts = [f'Kills: {k}', f'Deaths: {d}', f'Assists: {a}',f'CS/min: {csPerMin}']
    line_spacing = 20
    add_text_to_image(background, texts, text_color='white', outline_color='black', font_path='arial.ttf', font_size=85, line_spacing=line_spacing)

    name = [gamerTag]
    add_text_to_image(background, name, text_color='white', outline_color='black', font_path='arial.ttf', font_size=90, text_x=200, text_y=50)
    # Add the title. Change to red if GOMBOED, Green if good
    
    title = [msg]
    if (bad == True):
        add_text_to_image(background, title, text_color='red', outline_color='black', font_path='arial.ttf', font_size=80, text_x=10, text_y=600)
    else: 
        if (msg.startswith("Ultimate") or msg.startswith("Supreme")):
            add_text_to_image(background, title, text_color='#C89B3C', outline_color='black', font_path='arial.ttf', font_size=80, text_x=10, text_y=600)
        else:
            add_text_to_image(background, title, text_color='#90ee90', outline_color='black', font_path='arial.ttf', font_size=80, text_x=10, text_y=600)
         
    winningOrLost = [win]
    if win == True:
        add_text_to_image(background, "Win", text_color='#90ee90', outline_color='black', font_path='arial.ttf', font_size=80, text_x=900,text_y=60)
    else:
        add_text_to_image(background, "Loss", text_color='red', outline_color='black', font_path='arial.ttf', font_size=80, text_x=900, text_y=60)   
        
    title2 = [multikill]
    
    if multikill == "pentaKills":
        add_text_to_image(background, "PENTAKILL", text_color='white', outline_color='black', font_path='arial.ttf', font_size=75, text_x=1150,text_y=10, vertical=True)
  
    elif  multikill == "quadraKills":
        add_text_to_image(background, "QUADRA KILL", text_color='white', outline_color='black', font_path='arial.ttf', font_size=55, text_x=1150 ,text_y=25, vertical=True)
        
    elif  multikill == "tripleKills":
        add_text_to_image(background, "TRIPLE KILL", text_color='white', outline_color='black', font_path='arial.ttf', font_size=55, text_x=1150 ,text_y=25, vertical=True)
        
        
    background.save(output_image_path)
 
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
                
                if (gomfinder(k, d, a, kda, kp) != ""):
                    string = gomfinder(k, d, a, kda, kp) 
                    if penta >= 1:
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"pentaKills",win,csPerMin)
                    elif quadra >= 1:
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"quadraKills",win,csPerMin)
                    elif triple >= 1:
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"tripleKills",win,csPerMin)
                    else:    
                        generateImage(champ , keys_list[i] , playerInfo[0], string,k,d,a,kda,True,"",win,csPerMin)
                    await channelSend(keys_list[i])
                    
                elif gomfinder(k, d, a, kda, kp) == "":
                    string = bruhfinder(k,d,a,kda,kp) 
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