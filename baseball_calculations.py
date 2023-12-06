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
    calculate_stats_baseball("basketball_data.json", cur, conn)

if __name__ == "__main__":
    main()