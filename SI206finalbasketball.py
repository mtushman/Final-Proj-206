import unittest
import sqlite3
import json
import os
import requests
import time
import matplotlib.pyplot as plt


def get_basketball_info(url, params=None):
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


def create_table_players(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS basketball_players (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, position TEXT, height_feet INTEGER, height_inches INTEGER, weight_pounds INTEGER)')
    conn.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS basketball_stats (player_id INTEGER PRIMARY KEY, games_played INTEGER, reb NUMERIC, ast NUMERIC, pts NUMERIC)')
    conn.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS basketball_25_rows_4_times (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, position TEXT, height_feet INTEGER, height_inches INTEGER, weight_pounds INTEGER)')

def show_25_rows(cur, conn):
    cur.execute('SELECT COUNT(*) FROM basketball_25_rows_4_times')
    count_result = cur.fetchone()
    count = count_result[0] if count_result else 0
    start_page = (count // 25) + 1
    for index in range(start_page, 210):
        url = f'https://www.balldontlie.io/api/v1/players?page={index}'
        data = get_basketball_info(url)
        for player in data['data']:
            id = player['id']
            first_name = player['first_name']
            last_name = player['last_name']
            position = player['position']
            height_feet = player.get('height_feet', None)
            height_inches = player.get('height_inches', None)
            weight_pounds = player.get('weight_pounds', None)
            cur.execute("INSERT OR IGNORE INTO basketball_25_rows_4_times (id, first_name, last_name, position, height_feet, height_inches, weight_pounds) VALUES (?,?,?,?,?,?,?)", (id, first_name, last_name, position, height_feet, height_inches, weight_pounds))
            count += 1
            if count % 25 == 0:
                conn.commit()
                return
        if index in [60, 120, 180]:
            time.sleep(65)
    conn.commit()



def add_player(cur, conn):
    index=1
    while index<= 209:
        url = f'https://www.balldontlie.io/api/v1/players?page={index}'
        data = get_basketball_info(url)
        for player in data['data']:
            id = player['id']
            first_name = player['first_name']
            last_name = player['last_name']
            position = player['position']
            height_feet = player.get('height_feet', None)
            height_inches = player.get('height_inches', None)
            weight_pounds = player.get('weight_pounds', None)
            cur.execute("INSERT OR IGNORE INTO basketball_players (id, first_name, last_name, position, height_feet,height_inches, weight_pounds) VALUES (?,?,?,?,?,?,?)", (id, first_name, last_name, position, height_feet, height_inches, weight_pounds))
        index+=1
        if index == 60 or index == 120 or index == 180:
            time.sleep(65)
        conn.commit()

def add_stats(cur, conn):
    index = 0
    
    while index <= 5207:
        string= f"player_ids[]={index+1}&player_ids[]={index+2}&player_ids[]={index+3}&player_ids[]={index+4}&player_ids[]={index+5}&player_ids[]={index+6}&player_ids[]={index+7}&player_ids[]={index+8}&player_ids[]={index+9}&player_ids[]={index+10}&player_ids[]={index+11}&player_ids[]={index+12}&player_ids[]={index+13}&player_ids[]={index+14}&player_ids[]={index+15}&player_ids[]={index+16}&player_ids[]={index+17}&player_ids[]={index+18}&player_ids[]={index+19}&player_ids[]={index+20}"
        print(string)
        url=f"https://www.balldontlie.io/api/v1/season_averages?season=2022&{string}"
        data = get_basketball_info(url)
        if data == 'Exception':
            continue
        for player in data['data']:
            player_id = player['player_id']
            games_played = player['games_played']
            reb = player['reb']
            ast = player['ast']
            pts = player['pts']                
            cur.execute("INSERT OR IGNORE INTO basketball_stats (player_id, games_played, reb, ast, pts) VALUES (?,?,?,?,?)", (player_id, games_played, reb, ast, pts))
        index += 20
        conn.commit()
        if index%60==0:
            time.sleep(65)
        
def main():
    cur, conn = setUpDatabase('sport_analysis.db')  
    create_table_players(cur, conn)
    show_25_rows(cur, conn)
    add_player(cur,conn)
    add_stats(cur,conn)

if __name__ == "__main__":
    main()