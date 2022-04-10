#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 17:34:57 2021

@author: manpreet
"""

from flask import Flask, render_template, request, Response
import time
import json
from threading import Thread
import requests
import pandas as pd
from datetime import datetime
from f1_optimal_combo import get_round_number, list_of_possible_players
from f1_optimal_combo import get_df as df_to_html, NUM_OF_RACES

pd.set_option('display.width', 1000)
pd.set_option('colheader_justify', 'center')


def save_json(json_name, data):
    with open(json_name+'.json', 'w') as f:
        json.dump(data, f)
    print("saved ", json_name)

#%%
app = Flask(__name__)
teams_info = pd.read_csv('teams.csv')
drivers_info = pd.read_csv('drivers.csv')
combined_json = {}
parser = lambda date: datetime.strptime(date, '%d/%m/%y')
schedule = pd.read_csv('schedule.csv', parse_dates = ['dates'], date_parser = parser)

teams_info['avg'] = teams_info.total_points.apply(lambda x: x/NUM_OF_RACES)
drivers_info['avg'] = drivers_info.total_points.apply(lambda x: x/NUM_OF_RACES)

drivers = {}
for x in zip(drivers_info.cost.to_dict().values(), drivers_info.driver.to_dict().values(), drivers_info.total_points.to_dict().values()):
    drivers[x[1]] = {'cost': x[0], 'score': x[2]}

teams = {}
for x in zip(teams_info.cost.to_dict().values(), teams_info.teams.to_dict().values(), teams_info.total_points.to_dict().values()):
    teams[x[1]] = {'cost':x[0], 'score':x[2]}

avg_points = {}
for x in zip(teams_info.avg.to_dict().values(), teams_info.teams.to_dict().values()):
    avg_points[x[1]] = x[0]

for x in zip(drivers_info.avg.to_dict().values(), drivers_info.driver.to_dict().values()):
    avg_points[x[1]] = x[0]
    
finish_probability = {}
for x in zip(drivers_info.finished.to_dict().values(),drivers_info.total_races.to_dict().values(), drivers_info.driver.to_dict().values()): 
    finish_probability[x[2]] = x[0]/x[1]
    
for driver in drivers:
    combined_json[driver] = drivers[driver]

for team in teams:
    combined_json[team] = teams[team]
#%%
@app.route('/combos', methods=['POST'])
def third_party_call():
    #send an acknowledgement
    
    exclude_drivers = request.form.getlist('exclude')
    cost = float(request.form.getlist('cost')[0])
    include_drivers = request.form.getlist('include')
    include_team = request.form.get('include_team')
     
    combos = list_of_possible_players(drivers, teams, exclude_drivers, include_drivers, cost, include_team = include_team)
    combos.sort(key= lambda x: (x[4],x[5]), reverse=True)

    output_df = df_to_html(combos)
   
    # return Response(json.dumps({"status": "ok"}),status=200,  content_type='application/json')
    return output_df.to_html(justify='center')

@app.route('/view_cost')
def update():
    return render_template('update_cost.html', jsonfile=json.dumps(combined_json))


@app.route('/update', methods=['POST'])
def update_cost_price():
    for driver in drivers:
        this_driver_cost = request.form.get(driver + '_cost')
        this_driver_score = request.form.get(driver + '_score')
        if this_driver_cost is not None:
            drivers[driver]['cost'] = float(this_driver_cost)
        if this_driver_score is not None:
            drivers[driver]['score'] = float(this_driver_score)
        
    for team in teams:
        this_team_cost = request.form.get(team + '_cost')
        this_team_score = request.form.get(team + '_score')
        if this_team_cost is not None:
            teams[team]['cost'] = float(this_team_cost)
        if this_team_score is not None:
            teams[team]['score'] = float(this_team_score)
            
    save_json('teams', teams)
    save_json('drivers', drivers) 
    
    return render_template('main_page.html')


@app.route('/')
def index(text=None):
    return render_template('main_page.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
