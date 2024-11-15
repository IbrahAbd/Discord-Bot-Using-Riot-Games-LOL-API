import requests
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