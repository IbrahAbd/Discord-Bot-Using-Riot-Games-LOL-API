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