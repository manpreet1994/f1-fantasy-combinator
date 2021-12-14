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

exclude_drivers = []
#%%
app = Flask(__name__)
teams_info = pd.read_csv('teams.csv')
drivers_info = pd.read_csv('drivers.csv')
parser = lambda date: datetime.strptime(date, '%d/%m/%y')
schedule = pd.read_csv('schedule.csv', parse_dates = ['dates'], date_parser = parser)

NUM_OF_RACES = get_round_number(time.localtime()[2], time.localtime()[1])

teams_info['avg'] = teams_info.total_points.apply(lambda x: x/NUM_OF_RACES)
drivers_info['avg'] = drivers_info.total_points.apply(lambda x: x/NUM_OF_RACES)

drivers = {}
for x in zip(drivers_info.cost.to_dict().values(), drivers_info.driver.to_dict().values()):
    drivers[x[1]] = x[0]

teams = {}
for x in zip(teams_info.cost.to_dict().values(), teams_info.teams.to_dict().values()):
    teams[x[1]] = x[0]

avg_points = {}
for x in zip(teams_info.avg.to_dict().values(), teams_info.teams.to_dict().values()):
    avg_points[x[1]] = x[0]

for x in zip(drivers_info.avg.to_dict().values(), drivers_info.driver.to_dict().values()):
    avg_points[x[1]] = x[0]

def df_to_html(inp_combo, top_combination=25):
    data = {
        "driver1" : [],
        "driver2" : [],
        "driver3" : [],
        "driver4" : [],
        "driver5" : [],
        "Team" :[],
        "Budget" : [],
        "Avgpts" : []
        }

    for x in inp_combo[:top_combination]:
        driver_names = list(x[0])
        driver_names.sort()
        data["driver1"].append(driver_names[0])
        data["driver2"].append(driver_names[1])
        data["driver3"].append(driver_names[2])
        data["driver4"].append(driver_names[3])
        data["driver5"].append(driver_names[4])
        data["Team"].append(x[1])
        data["Budget"].append(x[2])
        data["Avgpts"].append(x[4])

    return pd.DataFrame(data)


@app.route('/combos', methods=['POST'])
def third_party_call():
    #send an acknowledgement
    cost = float(request.form['cost'])
    print("Total cost =", cost)
    combos = list_of_possible_players(drivers, teams, exclude_drivers, cost)
    combos.sort(key= lambda x: x[-1], reverse=True)

    output_df = df_to_html(combos)

    # return Response(json.dumps({"status": "ok"}),status=200,  content_type='application/json')
    return output_df.to_html()

@app.route('/')
def index(text=None):
    return render_template('main_page.html')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5005)
