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
from f1_optimal_combo import get_latest_details

pd.set_option('display.width', 1000)
pd.set_option('colheader_justify', 'center')


def save_json(json_name, data):
    with open(json_name+'.json', 'w') as f:
        json.dump(data, f)
    print("saved ", json_name)

#%%
app = Flask(__name__)


parser = lambda date: datetime.strptime(date, '%d/%m/%y')
schedule = pd.read_csv('schedule.csv', parse_dates = ['dates'], date_parser = parser)

#%%
@app.route('/combos', methods=['POST'])
def third_party_call():
    #send an acknowledgement
    drivers, teams, _ = get_latest_details()
    
    exclude_drivers = request.form.getlist('exclude')
    cost = float(request.form.getlist('cost')[0])
    include_drivers = request.form.getlist('include')
    include_team = request.form.get('include_team')
     
    combos = list_of_possible_players(drivers, teams, exclude_drivers, include_drivers, cost, include_team = include_team)
    
    # import pdb;pdb.set_trace()
    
    combos.sort(key= lambda x: (x[4],-x[5]), reverse=True)

    output_df = df_to_html(combos)
   
    # return Response(json.dumps({"status": "ok"}),status=200,  content_type='application/json')
    return output_df.to_html(justify='center')

@app.route('/view_cost')
def update():
    drivers, teams, _ = get_latest_details()
    combined_json = {}
    for driver in drivers:
        combined_json[driver] = drivers[driver]

    for team in teams:
        combined_json[team] = teams[team]
    
    return render_template('update_cost.html', jsonfile=json.dumps(combined_json))


@app.route('/update', methods=['POST'])
def update_cost_price():
    teams_info = pd.read_csv('teams.csv')
    drivers_info = pd.read_csv('drivers.csv')
    drivers, teams, _ = get_latest_details()
    
    for driver in drivers:
        this_driver_cost = request.form.get(driver + '_cost')
        this_driver_score = request.form.get(driver + '_score')
        this_driver_dnf = request.form.get(driver + '_dnf')
        #updating cost and score        
        drivers_info.loc[drivers_info.driver == driver, ['cost']] = this_driver_cost        
        drivers_info.loc[drivers_info.driver == driver, ['score']] = this_driver_score
        drivers_info.loc[drivers_info.driver == driver, ['dnf']] = this_driver_dnf

        
    for team in teams:
        this_team_cost = request.form.get(team + '_cost')
        this_team_score = request.form.get(team + '_score')
        
        #updating cost and score        
        teams_info.loc[teams_info.teams == team, ['cost']] = this_team_cost        
        teams_info.loc[teams_info.teams == team, ['score']] = this_team_score
        
            
    drivers_info.to_csv('drivers.csv', index=False)
    teams_info.to_csv('teams.csv', index=False)
    
    return render_template('main_page.html')


@app.route('/')
def index(text=None):
    return render_template('main_page.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
