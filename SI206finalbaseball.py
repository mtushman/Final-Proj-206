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
    cur.execute('CREATE TABLE IF NOT EXISTS baseball_25_rows_4_times (player_id INTEGER PRIMARY KEY, player_name TEXT, team_id INTEGER, team_name TEXT)')
    conn.commit()
    # cur.execute('DROP TABLE IF EXISTS baseball_25_rows_4_times')
    # conn.commit()


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
    
def show_25_rows(cur, conn):
    player_id_lst = []
    team_id_list = add_team()
    inserted_count = 0  # To keep track of the number of inserted rows

    # Fetch the current count from the database
    cur.execute('SELECT COUNT(*) FROM baseball_25_rows_4_times')
    count_result = cur.fetchone()
    current_count = count_result[0] if count_result else 0
    # print(current_count)
    if current_count==25:
        team_id_list.pop(0)
    elif current_count==50:
        team_id_list.pop(0)
        team_id_list.pop(0)
    elif current_count==75:
        team_id_list.pop(0)
        team_id_list.pop(0)
        team_id_list.pop(0)
    elif current_count>=100:
        return 'Already added 25 items 4 times'

    for team in team_id_list:
        if inserted_count >= 25:
            break  # Stop if 25 rows have already been inserted

        url = f"http://lookup-service-prod.mlb.com/json/named.roster_40.bam?team_id='{team}'"
        data = get_baseball_info(url)

        for player in data['roster_40']['queryResults']['row']:

            
            
            if inserted_count >= 25:
                break  # Stop if 25 rows have already been inserted

            player_id = player['player_id']
            player_name = player['name_display_first_last']
            team_id = player['team_id']
            team_name = player['team_name']
            player_id_lst.append(player_id)

            # Insert data into the database
            cur.execute('INSERT OR IGNORE INTO baseball_25_rows_4_times (player_id, player_name, team_id, team_name) VALUES(?, ?, ?, ?)', (player_id, player_name, team_id, team_name))
            conn.commit()
            inserted_count += 1

    return player_id_lst
        

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
        

def main():
    cur, conn = setUpDatabase('sport_analysis.db')
    create_tables(cur, conn)
    show_25_rows(cur, conn)
    add_player(cur,conn)
    add_stats(cur,conn)

if __name__ == "__main__":
    main()