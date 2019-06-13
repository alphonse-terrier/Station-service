# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from geograph import whereitis
from calculate import calculate
from grabbing_station import export_to_json

export_to_json()

PRICES_LIST = ["Gazole", "E10", "SP98", "E85", "GPLc", "SP95"]
center = (46.4833, 2.5333)
zoom = 4.5

mapbox_access_token = "pk.eyJ1IjoiYWxwaDQ5IiwiYSI6ImNqd25haHRmdTA1NW40M242Mmx3NjI4c3IifQ.u4lNPUHKy4je43P6xyjeXg"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://codepen.io/alphonse-terrier/pen/jogGzz.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([html.H1("Stations services les moins chères")],
             style={'textAlign': "center", "padding-bottom": "10", "padding-top": "10"}),

    html.Div([
        html.Label('Carburant'),
        dcc.Dropdown(
            options=[{'label': i, 'value': i} for i in PRICES_LIST],
            value='Gazole',
            id='fuel'
        )], style={'width': "100%"}),

    html.Div([
        html.Div([
            html.Label('Point de départ'),
            dcc.Input(value='55 Rue du Faubourg Saint-Honoré, 75008 Paris', type='text', id='depart')
        ], style={'width': "100%"}),
        html.Div([
            html.Label('Destination'),
            dcc.Input(value='38 Rue Jean Mermoz, 14804 Deauville', type='text', id='arrivee'),
        ], style={'width': "100%"}),
        html.Div([
            html.Label("Détour maximal (en km)"),
            dcc.Input(value='3', type='number', id='distance'),
        ], style={'width': "100%"}),
        html.Div([
            html.Label("Nombre de pompes à afficher"),
            dcc.Input(value='10', type='number', id='pompes'),
        ], style={'width': "100%"})
    ]
    ),
    html.Label(r''),

    html.Div([
        html.Button('Valider', id='button', value='1')
    ], style={'width': "100%"}),

    html.Div(dcc.Graph(id="my-graph"))
], className="container")


@app.callback(
    dash.dependencies.Output("button", 'n_clicks'),
    [dash.dependencies.Input("depart", "value"), dash.dependencies.Input("arrivee", "value"),
     dash.dependencies.Input("fuel", "value"), dash.dependencies.Input("distance", "value"),
     dash.dependencies.Input("pompes", "value")]
)
def reset_button(depart, arrivee, gasfuel, distance, pompes):
    return None


@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input("depart", "value"), dash.dependencies.Input("arrivee", "value"),
     dash.dependencies.Input("fuel", "value"), dash.dependencies.Input("button", 'n_clicks'),
     dash.dependencies.Input("distance", "value"), dash.dependencies.Input("pompes", "value")]
)
def update_figure(depart, arrivee, gasfuel, button, distance, pompes):
    trace = [go.Scattermapbox(lat=[None], lon=[None], mode='markers', text=[''])]

    if button is not None and depart is not None and arrivee is not None and gasfuel is not None and distance is not None and pompes is not None:
        coords = (whereitis(depart), whereitis(arrivee))
        trace.append(
            go.Scattermapbox(lat=[coords[0][0], coords[1][0]], lon=[coords[0][1], coords[1][1]], mode='markers',
                             marker={'symbol': "circle", 'size': 12, 'color': 'rgb(169, 204, 227)'},
                             text=[depart, arrivee], hoverinfo='text'))
        if coords[0][0] is not None and coords[1][0] is not None and coords[0][1] is not None and coords[1][
            1] is not None:
            df_station = calculate(coords, gasfuel, int(distance), int(pompes))
            df_station['nom'] = df_station['address'] + r'<br />' + df_station['codepostal'].astype(str) + ' ' + \
                                df_station['city'] + r'<br />Prix : ' + df_station['prix'].astype(float).round(
                3).astype(str) + ' euros'

            trace.append(
                go.Scattermapbox(lat=df_station["latitude"], lon=df_station["longitude"], mode='markers',
                                 marker={'symbol': "fuel", 'size': 11, 'color': 'rgb( 205, 92, 92 )'},
                                 text=df_station['nom'], hoverinfo='text'))
    return {"data": trace,
            "layout": go.Layout(autosize=True, hovermode='closest', showlegend=False, height=700,
                                mapbox={'accesstoken': mapbox_access_token, 'bearing': 0,
                                        'center': {'lat': center[0], 'lon': center[1]}, 'pitch': 0, 'zoom': zoom,
                                        "style": 'mapbox://styles/mapbox/streets-v9'})}


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
