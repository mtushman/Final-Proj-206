import unittest
import sqlite3
import json
import os
import requests
import time


def get_basketball_info(url, params=None):
    '''
    Check whether the 'params' dictionary has been specified. 
    Makes a request to access data with the 'url' and 'params' given, if any. 
    If the request is successful, return a dictionary representation 
    of the decoded JSON. If the search is unsuccessful, print out "Exception!"
    and return None.

    Parameters
    ----------
    url (str): a url that provides information about entities in the Star Wars universe.
    params (dict): optional dictionary of querystring arguments (default value is 'None').
        

    Returns
    -------
    dict: dictionary representation of the decoded JSON.
    '''
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
    cur.execute('CREATE TABLE IF NOT EXISTS b_players (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, position TEXT, height_feet INTEGER, height_inches INTEGER, weight_pounds INTEGER)')
    conn.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS b_stats (player_id INTEGER PRIMARY KEY, games_played INTEGER, reb NUMERIC, ast NUMERIC, pts NUMERIC)')
    conn.commit()


def add_player(cur, conn):
    index=1
    while index<= 209:
        url = f'https://www.balldontlie.io/api/v1/players?page={index}'
        data = get_basketball_info(url)
        # print(data)
        # print(data['data'])
        for player in data['data']:
            id = player['id']
            first_name = player['first_name']
            last_name = player['last_name']
            position = player['position']
            height_feet = player.get('height_feet', None)
            height_inches = player.get('height_inches', None)
            weight_pounds = player.get('weight_pounds', None)
            # cur.execute('INSERT OR IGNORE INTO b_players (id, first_name, last_name, position, height_feet, height_inches, weight_pounds) VALUES(?, ?, ?, ?, ?, ?, ?)', (id, first_name, last_name, position, height_feet, height_inches, weight_pounds))
            cur.execute("INSERT OR IGNORE INTO b_players (id, first_name, last_name, position, height_feet,height_inches, weight_pounds) VALUES (?,?,?,?,?,?,?)", (id, first_name, last_name, position, height_feet, height_inches, weight_pounds))
        index+=1
        conn.commit()
        if index == 60 or index == 120 or index == 180:
            time.sleep(65)

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
            cur.execute("INSERT OR IGNORE INTO b_stats (player_id, games_played, reb, ast, pts) VALUES (?,?,?,?,?)", (player_id, games_played, reb, ast, pts))
        index += 20
        conn.commit()
        if index%60==0:
            time.sleep(65)
        


# def create_table_stats():


def main():
    cur, conn = setUpDatabase('basketball_players.db')
    create_table_players(cur, conn)
    # add_player(cur,conn)
    # add_stats(cur,conn)

if __name__ == "__main__":
    main()