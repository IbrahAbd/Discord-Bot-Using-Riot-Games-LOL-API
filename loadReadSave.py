from RiotAPI import puuidPairs,filename
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