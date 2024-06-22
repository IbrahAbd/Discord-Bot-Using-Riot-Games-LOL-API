# Automated-Discord-Bot-Using-Riot-Games-LOL-API

This Python program takes in several parameters from the RIOT API for league of legends (LOL) by parsing JSON responses to get the needed data.  

# Image generation 
The most recent game is processed and an image is generated every 15 minutes if a new game has been played.  
The image consists of:  

1. The profile picture of the player.
2. The name of the player.
3. The kills the player achieved in the game.
4. The deaths the player achieved in the game.
5. The assists the player achieved in the game.
6. The CS/min (creep score per minute) achived within the game.
7. A classification on their performance in the game.
8. If the game was won/lost.
9. If a multikill was achieved such as a Penta/Quadra/Triple Kill.
10. A random splash art is used as backround for the champion played within the game.

The below generated image is the example of the above:  

<img src="https://github.com/IbrahAbd/Discord-Bot-Using-Riot-Games-LOL-API/blob/main/Ibrahim.jpg" width="500" height="300">

# Bot commands
The bot also provides 4 commands that the user can input:  
1. #kills  
2. #assists  
3. #deaths  
4. #mastery <username> <num>  

#kills - outputs the kill leaderboard from tracked games.  
#assists - outputs the assist leaderboard from tracked games.  
#deaths -  outputs the death leaderboard from tracked games.  
#mastery username num - Outputs the top "num" champion mastery of "username"   
The above username HAS to be in the puuidPairs.txt file.  

An example of this is:  
#mastery Bruh 5  
  
Which returns the following:  

Top 5 champion masteries for Bruh:

1.) Kaisa, Mastery Level: 11, Mastery Points: 129173

2.) Aphelios, Mastery Level: 8, Mastery Points: 77475

3.) Caitlyn, Mastery Level: 8, Mastery Points: 73099

4.) MissFortune, Mastery Level: 7, Mastery Points: 62171

5.) Jinx, Mastery Level: 7, Mastery Points: 55994

# <u>**What you need to change:**</u>

1. The records in puuidPairs.txt are hardcoded to the users as it avoids unnessary processing and requests every time the program is run. You will need to change this to cater to your users/friends by getting their puuids etc. I have left my details for reference on stucture. 
2. The.env file will need to be changed to add your discord bot key given on the developer site.
3. The RIOT API key needs to be updated.
4. The discord Channel IDs need to be updated to the desired ones.
5. You will also have to add the user's profile pictures manually or automate it if you wish.


(All splash arts are RIOT games properly and are accessed under the appropriate licenses.)


