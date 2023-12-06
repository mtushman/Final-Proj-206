import unittest
import sqlite3
import json
import os
import requests
import time
import matplotlib.pyplot as plt


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn



def calculate_stats_basketball(filename, cur, conn):
    #get the stats for a player by joining the two tables
    cur.execute("SELECT basketball_players.first_name, basketball_players.last_name, basketball_stats.pts, basketball_stats.ast, basketball_stats.reb FROM basketball_players JOIN basketball_stats ON basketball_players. id = basketball_stats.player_id")
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
    #get the league average for each stat
    league_pts_average= sum(pts_lst)/len(pts_lst)
    league_ast_average= sum(ast_lst)/len(ast_lst)
    league_reb_average= sum(reb_lst)/len(reb_lst)
    print(league_pts_average)
    print(league_ast_average)
    print(league_reb_average)
    #new lists for the players that cross the tresholds
    above_pts=[]
    above_ast=[]
    above_reb=[]
    elite=[]
    #each statement gets the name and stat of the threshold they crossed
    cur.execute("SELECT basketball_players.first_name, basketball_players.last_name, basketball_stats.pts FROM basketball_players JOIN basketball_stats ON basketball_players.id = basketball_stats.player_id WHERE pts > 11.13")
    res = cur.fetchall()
    print(res)
    above_pts.append(res)
    cur.execute("SELECT basketball_players.first_name, basketball_players.last_name, basketball_stats.ast FROM basketball_players JOIN basketball_stats ON basketball_players.id = basketball_stats.player_id WHERE ast > 2.57")
    res = cur.fetchall()
    print(res)
    above_ast.append(res)
    cur.execute("SELECT basketball_players.first_name, basketball_players.last_name, basketball_stats.reb FROM basketball_players JOIN basketball_stats ON basketball_players.id = basketball_stats.player_id WHERE reb > 4.20")
    res = cur.fetchall()
    print(res)
    above_reb.append(res)
    #check for player and their stat if they crossed all three thresholds
    cur.execute("SELECT basketball_players.first_name, basketball_players.last_name, basketball_stats.pts, basketball_stats.ast, basketball_stats.reb FROM basketball_players JOIN basketball_stats ON  basketball_players.id = basketball_stats.player_id WHERE pts > 11.13 AND ast > 2.75 AND reb > 4.20")
    res = cur.fetchall()
    print(res)
    elite.append(res)

    count_above_average= len(above_pts[0])+len(above_ast[0])+len(above_reb[0])
    count_elite_player= len(elite[0])

    pts_percentage= (len(above_pts[0])/(len(all_players_lst)))*100
    ast_percentage= (len(above_ast[0])/(len(all_players_lst)))*100
    reb_percentage= (len(above_reb[0])/(len(all_players_lst)))*100
    elite_percentage= (len(elite[0])/(len(all_players_lst)))*100

    #write the information to the file
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
    
    #create charts of the data
    categories = ['elite', 'league average']
    values = [count_elite_player, count_above_average]
    colors = ['blue', 'green']

    plt.bar(categories, values, color=colors)
    plt.xlabel('Category of player')
    plt.ylabel('Amount of players')
    plt.title('Elite vs Above Average Player Counts - Basketball')
    plt.show()
    
    labels = ['Total Player', 'Players Above Average - pts']
    sizes = [len(all_players_lst)-len(above_pts[0]), len(above_pts[0])]
    colors = ['lightcoral', 'lightgreen']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean For Points Per Game vs Below")
    plt.show()

    labels = ['Total Player', 'Players Above Average - reb']
    sizes = [len(all_players_lst)-len(above_reb[0]), len(above_reb[0])]
    colors = ['lightcoral', 'orange']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, shadow=True)
    plt.title("Percentage of Players Above The League Mean for Rebounds Per Game Game vs Below")
    plt.show()

    labels = ['Total Player', 'Players Above Average - ast']
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
    calculate_stats_basketball("basketball_data.json", cur, conn)

    

if __name__ == "__main__":
    main()