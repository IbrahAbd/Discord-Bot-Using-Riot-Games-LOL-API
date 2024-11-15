from typing import Final
from PIL import Image, ImageDraw, ImageFont
import asyncio
import os
import requests
import math
import json
import logging
import random
import discord

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
 