import unittest
import sqlite3
import json
import os
import requests
import time
import matplotlib.pyplot as plt


def get_baseball_info(url, params=None):
    if params:
        try:
            response = requests.get(url, params)
            data = response.text
            return json.loads(data)
        except:
            print("Exception!")
            return None
    else:
        try:
            response = requests.get(url, params)
            data = response.text
            return json.loads(data)
        except:
            print("Exception!")
            return None

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn


def create_tables(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS baseball_players (player_id INTEGER PRIMARY KEY, player_name TEXT, team_id INTEGER, team_name TEXT)')
    conn.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS baseball_stats (player_id INTEGER PRIMARY KEY, player_avg NUMERIC, player_ops NUMERIC, player_obp NUMERIC)')
    conn.commit()


def add_team(): 
    team_id_lst=[]
    index = 1
    while index <= 30:
        data = get_baseball_info(f"http://lookup-service-prod.mlb.com/json/named.team_all_season.bam?sport_code='mlb'&all_star_sw='N'&sort_order=name_asc&season='2022'")
        count = 1
        for team in data['team_all_season']['queryResults']['row']:
            count += 1
            team_id = team['mlb_org_id']
            team_id_lst.append(team_id)
            index += 1
            if count%25 == 0:
                time.sleep(5)
        return(team_id_lst)
        

def add_player(cur, conn):
    player_id_lst=[]
    count=1
    ids= add_team()
    for id in ids:
        url = f"http://lookup-service-prod.mlb.com/json/named.roster_40.bam?team_id='{id}'"
        data = get_baseball_info(url)
        for player in data['roster_40']['queryResults']['row']:
            player_id = player['player_id']
            player_name = player['name_display_first_last']
            team_id = player['team_id']
            team_name= player['team_name']
            player_id_lst.append(player_id)
            cur.execute('INSERT OR IGNORE INTO baseball_players (player_id, player_name, team_id, team_name) VALUES(?, ?, ?, ?)', (player_id, player_name, team_id, team_name))
            count+=1
            conn.commit()
            if count%25 == 0:
                time.sleep(5)
    return player_id_lst

def add_stats(cur, conn):
    player_ids = add_player(cur, conn)
    count = 1

    for id in player_ids:
        url = f"http://lookup-service-prod.mlb.com/json/named.sport_hitting_tm.bam?league_list_id='mlb'&game_type='R'&season='2022'&player_id='{id}'"
        data = get_baseball_info(url)

        if 'row' not in data['sport_hitting_tm']['queryResults']:
            continue

        # Directly access the 'row' dictionary
        player_stats = data['sport_hitting_tm']['queryResults']['row']
        #Checking if the dictionary is not empty
        if type(player_stats)==dict:
            player_id = id
            player_avg = player_stats.get('avg', None)
            player_ops = player_stats.get('ops', None)
            player_obp = player_stats.get('obp', None)

            cur.execute("INSERT OR IGNORE INTO baseball_stats (player_id, player_avg, player_ops, player_obp) VALUES (?,?,?,?)", (player_id, player_avg, player_ops, player_obp))
            conn.commit()

        count += 1
        if count % 25 == 0:
            time.sleep(5)
        


def calculate_stats_baseball(filename, cur, conn):
    #get the stats for a player by joining the two tables
    cur.execute("SELECT baseball_players.player_name, baseball_stats.player_avg, baseball_stats.player_ops, baseball_stats.player_obp FROM baseball_players JOIN baseball_stats ON baseball_players.player_id = baseball_stats.player_id")
    res = cur.fetchall()
    all_players_lst = []
    avr_lst=[]
    obp_lst=[]
    ops_lst=[]
    for player in res:
        name = player[0]
        avr= player[1]
        ops= player[2]
        obp= player[3]
        #some players did not hit or were pitchers so did not include them
        if avr == '.---' or obp == '.---' or ops == '.---':
            continue
        else:
            avr_lst.append(avr)
            obp_lst.append(obp)
            ops_lst.append(ops)
            all_players_lst.append(name)
    #get the league average for each stat
    league_avr_average= sum(avr_lst)/len(avr_lst)
    league_obp_average= sum(obp_lst)/len(obp_lst)
    league_ops_average= sum(ops_lst)/len(ops_lst)
    print(league_avr_average)
    print(league_obp_average)
    print(league_ops_average)
    #new lists for the players that cross the tresholds
    above_avr=[]
    above_obp=[]
    above_ops=[]
    elite=[]
    #each statement gets the name and stat of the threshold they crossed
    cur.execute("SELECT baseball_players.player_name, baseball_stats.player_avg FROM baseball_players JOIN baseball_stats ON baseball_players.player_id = baseball_stats.player_id WHERE player_avg > 0.237 AND player_avg !='.---'")
    res = cur.fetchall()
    print(res)
    above_avr.append(res)
    cur.execute("SELECT baseball_players.player_name, baseball_stats.player_obp FROM baseball_players JOIN baseball_stats ON baseball_players.player_id = baseball_stats.player_id WHERE player_obp > 0.307 AND player_obp !='.---'")
    res = cur.fetchall()
    print(res)
    above_obp.append(res)
    cur.execute("SELECT baseball_players.player_name, baseball_stats.player_ops FROM baseball_players JOIN baseball_stats ON baseball_players.player_id = baseball_stats.player_id WHERE player_ops > 0.691")
    res = cur.fetchall()
    print(res)
    above_ops.append(res)
    #check for player and their stat if they crossed all three thresholds
    cur.execute("SELECT baseball_players.player_name, baseball_stats.player_avg, baseball_stats.player_ops, baseball_stats.player_obp FROM baseball_players JOIN baseball_stats ON baseball_players.player_id = baseball_stats.player_id WHERE player_avg > 0.237 AND player_obp > 0.307 AND player_ops > 0.691")
    res = cur.fetchall()
    print(res)
    elite.append(res)

    count_above_average= len(above_avr[0])+len(above_obp[0])+len(above_ops[0])
    count_elite_player= len(elite[0])

    average_percentage= (len(above_avr[0])/(len(all_players_lst)))*100
    obp_percentage= (len(above_obp[0])/(len(all_players_lst)))*100
    ops_percentage= (len(above_ops[0])/(len(all_players_lst)))*100
    elite_percentage= (len(elite[0])/(len(all_players_lst)))*100

    #write the information to the file
    with open(filename, 'w') as file:
        
        file.write("Total amount of players in Database " + str(len(all_players_lst)))
        file.write('\n\n\n')
        json.dump(above_avr, file)
        file.write("\nTotal amount of players above the league mean for Hitting Avergage: " + str(len(above_avr[0])))
        file.write("\nPercentage of players above the league mean for Hitting Avergage: " + str(average_percentage)+'%')
        file.write('\n\n\n')
        json.dump(above_obp, file)
        file.write("\nTotal amount of players above the league mean for OBP: " + str(len(above_obp[0])))
        file.write("\nPercentage of players above the league mean for OBP: " + str(obp_percentage)+'%')
        file.write('\n\n\n')
        json.dump(above_ops, file)
        file.write("\nTotal amount of players above the league mean for OPS: " + str(len(above_ops[0])))
        file.write("\nPercentage of players above the league mean for OPS: " + str(ops_percentage)+'%')
        file.write('\n\n\n')
        json.dump(elite, file)
        file.write("\nTotal amount of Elite players- above the league mean for for every category (avg, obp, ops): " + str(len(elite[0])))
        file.write("\nPercentage of Elite players: " + str(elite_percentage)+'%')
    
    #create charts of the data
    categories = ['elite', 'league average']
    values = [count_elite_player, count_above_average]
    colors = ['blue', 'green']
    
    plt.bar(categories, values, color=colors)
    plt.xlabel('Category of player')
    plt.ylabel('Amount of players')
    plt.title('Elite vs Above Average Player Counts - Baseball')
    plt.show()
    
    labels = ['Total Player', 'Players Above Average - avg']
    sizes = [len(all_players_lst)-len(above_avr[0]), len(above_avr[0])]
    colors = ['lightcoral', 'lightgreen']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean For Hitting Average vs Below")
    plt.show()

    labels = ['Total Player', 'Players Above Average - ops']
    sizes = [len(all_players_lst)-len(above_ops[0]), len(above_ops[0])]
    colors = ['lightcoral', 'orange']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players above the league mean for ops vs below")
    plt.show()

    labels = ['Total Player', 'Players Above Average - obp']
    sizes = [len(all_players_lst)-len(above_obp[0]), len(above_obp[0])]
    colors = ['lightcoral', 'purple']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean For OBP vs Below")
    plt.show()

    labels = ['Total Player', 'Elite Players']
    sizes = [len(all_players_lst)-len(elite[0]), len(elite[0])]
    colors = ['lightcoral', 'yellow']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Elite Players vs Non-Elite Players")
    plt.show()

def main():
    cur, conn = setUpDatabase('sport_analysis.db')
    create_tables(cur, conn)
    add_player(cur,conn)
    add_stats(cur,conn)
    calculate_stats_baseball("baseball_data.json", cur,conn)

if __name__ == "__main__":
    main()