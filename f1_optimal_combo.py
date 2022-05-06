# -*- coding: utf-8 -*-
"""
Spyder Editor

"""
#%%
import argparse
import pandas as pd
import time
from datetime import datetime
import numpy as np

parser = argparse.ArgumentParser(description='Shows combinations of drivers based on avg points on playon')

parser.add_argument('--cost', metavar='t', type=float, help='Total Cost of the team',default=100.0)

parser.add_argument('--combo', metavar='c', type=int, help='Total combinations', default=25)

parser.add_argument('--exclude', metavar='ex', type=str, help='Exclude drivers in comma separated format', default='')

args = parser.parse_args()

TOTAL_COST = args.cost
top_combination = args.combo

teams_info = pd.read_csv('teams.csv')
drivers_info = pd.read_csv('drivers.csv')

# teams_info = pd.read_json('teams.json')
# drivers_info = pd.read_json('drivers.json')

exclude_drivers = [x.strip() for x in args.exclude.split(',')]

include_drivers = [x.strip() for x in args.exclude.split(',')]

#schedule['date'] = schedule.dates.apply(lambda x: int(x.split("/")[0]))
#schedule['month'] = schedule.dates.apply(lambda x: int(x.split("/")[1]))

#%%

parser = lambda date: datetime.strptime(date, '%d/%m/%y')
schedule = pd.read_csv('schedule.csv', parse_dates = ['dates'], date_parser = parser)

def get_round_number(todays_date, todays_month):
    current_date = '2022'+'-'+str(todays_month)+'-'+str(todays_date)
    try:
        ans = schedule.loc[schedule.dates <= str(current_date)].index[-1]
    except:
        ans = 20
    return  ans + 1
    

#%%
NUM_OF_RACES = get_round_number(time.localtime()[2], time.localtime()[1])

# teams_info['avg'] = teams_info.score.apply(lambda x: x/NUM_OF_RACES)
# drivers_info['avg'] = drivers_info.score.apply(lambda x: x/NUM_OF_RACES)
#%%

def get_latest_details():
    teams_info = pd.read_csv('teams.csv')
    drivers_info = pd.read_csv('drivers.csv')
    
    teams_info['avg'] = teams_info.score.apply(lambda x: x/NUM_OF_RACES)
    drivers_info['avg'] = drivers_info.score.apply(lambda x: x/NUM_OF_RACES)
    
    drivers = {}
    
    for x in zip(drivers_info.cost.to_dict().values(), drivers_info.driver.to_dict().values(), drivers_info.score.to_dict().values(), drivers_info.dnf.to_dict().values()):
        drivers[x[1]] = {'cost': x[0], 'score': x[2], 'dnf': x[3]}
        
    teams = {}
    for x in zip(teams_info.cost.to_dict().values(), teams_info.teams.to_dict().values(), teams_info.score.to_dict().values()):
        teams[x[1]] = {'cost':x[0], 'score':x[2]}
        
    avg_points = {}
    for x in zip(teams_info.avg.to_dict().values(), teams_info.teams.to_dict().values()): 
        avg_points[x[1]] = x[0]
        
    for x in zip(drivers_info.avg.to_dict().values(), drivers_info.driver.to_dict().values()): 
        avg_points[x[1]] = x[0]
        
    # finish_probability = {}
    # for x in zip(drivers_info.finished.to_dict().values(),drivers_info.total_races.to_dict().values(), drivers_info.driver.to_dict().values()): 
    #     finish_probability[x[2]] = x[0]/x[1]
        
    return drivers, teams, avg_points
    

#%%
import itertools
# def findsubsets(s, n):
def findsubsets(s, n):
    return [set(i) for i in itertools.combinations(s, n)]

#%%
def list_of_possible_players(drivers, teams, player_exclusion, player_inclusion, TOTAL_COST, tolerance=None, include_team = ""):
    lineup = []
    
    drivers, teams, avg_points = get_latest_details()

    for comb in (findsubsets(drivers, 5)):
        for team in teams:
            temp_sum = sum([drivers[x]['cost'] for x in comb]) + teams[team]['cost']
            likely_avg_scores = (sum(avg_points[x] for x in comb) + avg_points[team])/NUM_OF_RACES
            # likely_finish_prob = np.prod([finish_probability[x] for x in comb])
            dnf_sum = sum([drivers[x]['dnf'] for x in comb])
            if temp_sum <= TOTAL_COST :
                lineup.append((comb, team, temp_sum, TOTAL_COST - temp_sum, 
                               likely_avg_scores, dnf_sum))
                
    for players in player_exclusion:
        lineup = [x for x in lineup if players not in x[0]]
    
    for players in player_inclusion:
        lineup = [x for x in lineup if players in x[0]]
    
    if include_team != "":     
        # print("team = ", list(set([x[0] for x in lineup])))
        lineup = [x for x in lineup if x[1] == include_team]
        
    return lineup

#%%
def get_df(combos, top_combination=25):
    data = {
        "dr1" : [],
        "dr2" : [],
        "dr3" : [],
        "dr4" : [],
        "dr5" : [],
        "Team" :[],
        "Budget" : [],
        "Avgpts" : [],
        "DNF" : []
        }
    
    
    for x in combos[:top_combination]:
        driver_names = list(x[0])
        driver_names.sort()
        data["dr1"].append(driver_names[0])
        data["dr2"].append(driver_names[1])
        data["dr3"].append(driver_names[2])
        data["dr4"].append(driver_names[3])
        data["dr5"].append(driver_names[4])
        data["Team"].append(x[1])
        data["Budget"].append(x[2])
        data["Avgpts"].append(x[4])
        data["DNF"].append(x[5])
            
    return pd.DataFrame(data)

#%%
if __name__ == "__main__":
    combos = list_of_possible_players(drivers, teams, exclude_drivers, include_drivers, TOTAL_COST, include_team= "haas")
    combos.sort(key= lambda x: (x[4],x[5]), reverse=True)
    print(get_df(combos))
    