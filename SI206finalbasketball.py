import unittest
import sqlite3
import json
import os
import requests
import time
import matplotlib.pyplot as plt


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
        
def calculate_stats_baseball(filename, cur, conn):
    cur.execute("SELECT b_players.first_name, b_players.last_name, b_stats.pts, b_stats.ast, b_stats.reb FROM b_players JOIN b_stats ON b_players. id = b_stats.player_id")
    res = cur.fetchall()
    print(res)
    pts_lst=[]
    ast_lst=[]
    reb_lst=[]
    all_players_lst = []
    # print(res)
    for player in res:
        name = player[0] + player[1]
        pts= player[2]
        ast= player[3]
        reb= player[4]
        pts_lst.append(pts)
        ast_lst.append(ast)
        reb_lst.append(reb)
        all_players_lst.append(name)
    league_pts_average= sum(pts_lst)/len(pts_lst)
    league_ast_average= sum(ast_lst)/len(ast_lst)
    league_reb_average= sum(reb_lst)/len(reb_lst)
    print(league_pts_average)
    print(league_ast_average)
    print(league_reb_average)
    above_pts=[]
    above_ast=[]
    above_reb=[]
    elite=[]
    cur.execute("SELECT b_players.first_name, b_players.last_name, b_stats.pts FROM b_players JOIN b_stats ON b_players.id = b_stats.player_id WHERE pts > 11.13")
    res = cur.fetchall()
    print(res)
    above_pts.append(res)
    cur.execute("SELECT b_players.first_name, b_players.last_name, b_stats.ast FROM b_players JOIN b_stats ON b_players.id = b_stats.player_id WHERE ast > 2.57")
    res = cur.fetchall()
    print(res)
    above_ast.append(res)
    cur.execute("SELECT b_players.first_name, b_players.last_name, b_stats.reb FROM b_players JOIN b_stats ON b_players.id = b_stats.player_id WHERE reb > 4.20")
    res = cur.fetchall()
    print(res)
    above_reb.append(res)
    cur.execute("SELECT b_players.first_name, b_players.last_name, b_stats.pts, b_stats.ast, b_stats.reb FROM b_players JOIN b_stats ON  b_players.id = b_stats.player_id WHERE pts > 11.13 AND ast > 2.75 AND reb > 4.20")
    res = cur.fetchall()
    print(res)
    elite.append(res)

    count_above_average= len(above_pts[0])+len(above_ast[0])+len(above_reb[0])
    count_elite_player= len(elite[0])
    # print(count_above_average)
    # print(count_elite_player)


    pts_percentage= (len(above_pts[0])/(len(all_players_lst)))*100
    ast_percentage= (len(above_ast[0])/(len(all_players_lst)))*100
    reb_percentage= (len(above_reb[0])/(len(all_players_lst)))*100
    elite_percentage= (len(elite[0])/(len(all_players_lst)))*100

    
    with open(filename, 'w') as file:
        file.write("Total amount of players in Database " + str(len(all_players_lst)))
        file.write('\n\n\n')
        json.dump(above_pts, file)
        file.write("\nTotal amount of players above the league mean for Points Per Game: " + str(len(above_pts[0])))
        file.write("\nPercentage of players above the league mean for Points Per Game: " + str(pts_percentage)+'%')
        file.write('\n\n\n')
        json.dump(above_ast, file)
        file.write("\nTotal amount of players above the league mean for Assists Per Game: " + str(len(above_ast[0])))
        file.write("\nPercentage of players above the league mean for Assists Per Game: " + str(ast_percentage)+'%')
        file.write('\n\n\n')
        json.dump(above_reb, file)
        file.write("\nTotal amount of players above the league mean for Rebounds Per Game: " + str(len(above_reb[0])))
        file.write("\nPercentage of players above the league mean for Rebounds Per Game: " + str(reb_percentage)+'%')
        file.write('\n\n\n')
        json.dump(elite, file)
        file.write("\nTotal amount of Elite players- above the league mean for for every category (pts, ast, reb): " + str(len(elite[0])))
        file.write("\nPercentage of Elite players: " + str(elite_percentage)+'%')
       
    categories = ['elite', 'league average']
    values = [count_elite_player, count_above_average]
    colors = ['blue', 'green']

    plt.bar(categories, values, color=colors)
    plt.xlabel('Category of player')
    plt.ylabel('Amount of players')
    plt.title('Elite vs Above Average Player Counts - Basketball')
    plt.show()
    
    labels = ['Total Player', 'pts']
    sizes = [len(all_players_lst)-len(above_pts[0]), len(above_pts[0])]
    colors = ['lightcoral', 'lightgreen']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean For Points Per Game vs Below")
    plt.show()

    labels = ['Total Player', 'reb']
    sizes = [len(all_players_lst)-len(above_reb[0]), len(above_reb[0])]
    colors = ['lightcoral', 'orange']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean for Rebounds Per Game Game vs Below")
    plt.show()

    labels = ['Total Player', 'ast']
    sizes = [len(all_players_lst)-len(above_ast[0]), len(above_ast[0])]
    colors = ['lightcoral', 'purple']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean For Assists Per Game vs Below")
    plt.show()

    labels = ['Total Player', 'Elite Players']
    sizes = [len(all_players_lst)-len(elite[0]), len(elite[0])]
    colors = ['lightcoral', 'yellow']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Elite Players vs Non-Elite Players")
    plt.show()

def main():
    cur, conn = setUpDatabase('sport_analysis.db')  
    # create_table_players(cur, conn)
    # add_player(cur,conn)
    # add_stats(cur,conn)
    calculate_stats_baseball("basketball_data.json", cur, conn)

if __name__ == "__main__":
    main()