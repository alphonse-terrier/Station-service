# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import dash
import us
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

PRICES_LIST = ["Gazole", "E10", "SP98", "E85", "GPLc", "SP95"]

mapbox_access_token = "pk.eyJ1IjoiYWxwaDQ5IiwiYSI6ImNqd25haHRmdTA1NW40M242Mmx3NjI4c3IifQ.u4lNPUHKy4je43P6xyjeXg"

df1 = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv")
df = df1.dropna(axis=0)

app_name = 'dash-scattermapboxplot'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

liste_fuel = []
for fuel in PRICES_LIST:
    liste_fuel.append({'label': fuel, 'value': fuel.lower()})

app.layout = html.Div([
    html.Div([html.H1("Stations services les moins chères")],
             style={'textAlign': "center", "padding-bottom": "10", "padding-top": "10"}),

    html.Div([
        html.Label('Carburant'),
        dcc.Dropdown(
            options=[{'label': i, 'value': i.lower()} for i in PRICES_LIST],
            value='gazole'
        ), html.Label('Point de départ'),
        dcc.Input(value='55 Rue du Faubourg Saint-Honoré, 75008 Paris', type='text'),

        html.Label('Destination'),
        dcc.Input(value='38 Rue Jean Mermoz, 14804 Deauville', type='text')]),

    html.Div([dcc.Dropdown(id="state-selected", value=['CA'], multi=True,
                           options=[{'label': f'{us.states.lookup(i)}', 'value': i} for i in df.state.unique()],
                           style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "50%"})]),
    html.Div(dcc.Graph(id="my-graph"))
], className="container")


@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [dash.dependencies.Input("state-selected", "value")])
def update_figure(selected):
    trace = []
    for state in selected:
        dff = df[df["state"] == state]
        trace.append(
            go.Scattermapbox(lat=dff["lat"], lon=dff["long"], mode='markers', marker={'symbol': "fuel", 'size': 10},
                             text=dff['airport'], hoverinfo='text', name=state))
    return {"data": trace,
            "layout": go.Layout(autosize=True, hovermode='closest', showlegend=False, height=700,
                                mapbox={'accesstoken': mapbox_access_token, 'bearing': 0,
                                        'center': {'lat': 46.4833, 'lon': 2.5333}, 'pitch': 0, 'zoom': 4.5,
                                        "style": 'mapbox://styles/mapbox/light-v9'})}


if __name__ == '__main__':
    app.run_server(debug=True)
