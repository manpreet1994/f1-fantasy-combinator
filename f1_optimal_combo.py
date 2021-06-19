# -*- coding: utf-8 -*-
"""
Spyder Editor

"""
#%%
import json
import argparse


parser = argparse.ArgumentParser(description='Shows combinations of drivers based on avg points on playon')

parser.add_argument('--cost', metavar='t', type=float, help='Total Cost of the team',default=100.0)

parser.add_argument('--combo', metavar='c', type=int, help='Total combinations', default=25)

args = parser.parse_args()

TOTAL_COST = args.cost
top_combination = args.combo

# TOTAL_COST = 100.0
# top_combination = 25

f = open('config.json')

params = json.load(f)
#%%

player_exclusion = params["exclude"]

drivers = params["drivers"]

teams = params["teams"]

avg_points = params["avg_points"]

#%%
import itertools
# def findsubsets(s, n):
def findsubsets(s, n):
    return [set(i) for i in itertools.combinations(s, n)]

#%%
def list_of_possible_players(drivers, teams, player_exclusion,TOTAL_COST, tolerance=None):
    lineup = []
    for comb in (findsubsets(drivers, 5)):
        for team in teams:
            temp_sum = sum([drivers[x] for x in comb]) + teams[team]
            likely_avg_scores = sum(avg_points[x] for x in comb) + avg_points[team]
            if temp_sum <= TOTAL_COST:
                lineup.append((comb, team, temp_sum, TOTAL_COST - temp_sum, likely_avg_scores))
    for players in player_exclusion:
        lineup = [x for x in lineup if players not in x[0]]

    return lineup

#%%
combos = list_of_possible_players(drivers, teams, player_exclusion, TOTAL_COST)
combos.sort(key= lambda x: x[-1], reverse=True)

#%%
import pandas as pd
data = {
        "dr1" : [],
        "dr2" : [],
        "dr3" : [],
        "dr4" : [],
        "dr5" : [],
        "Team" :[],
        "Budget" : [],
        "Avgpts" : []
        }
#%%
for x in combos[:top_combination]:
    driver_names = list(x[0])
    data["dr1"].append(driver_names[0])
    data["dr2"].append(driver_names[1])
    data["dr3"].append(driver_names[2])
    data["dr4"].append(driver_names[3])
    data["dr5"].append(driver_names[4])
    data["Team"].append(x[1])
    data["Budget"].append(x[2])
    data["Avgpts"].append(x[4])    

df = pd.DataFrame(data) 
print(df)