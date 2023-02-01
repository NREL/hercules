# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import logging
import os
import pathlib
import sys
import numpy as np
import pandas as pd
import datetime as dt
import sqlite3
from contextlib import closing
import plotly.express as px
import dash
from dash import dcc, html
import dash_daq as daq
from db import get_data, insert_data, get_turbine_locs
from skimage import io
# from nwtc import get_latest_wind_data

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State


#PARAMETERS
num_turbines = 4

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 1000)

# Set up the logger
# Useful for when running on eagle
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    filename='log_front_end.log',
                    filemode='w')
logger = logging.getLogger('log_front_end')

# Perhaps a small hack to also send log to the terminal output 
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# Initial values
wind_speed_init = 8
wind_direction_init = 270

# Get the turbine locs
x_locs, y_locs = get_turbine_locs()
num_turbines = len(x_locs)

# Force this for now
D = 126.


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Transmission Emulator Dashboard"

server = app.server

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

app_color = {"primary": "#00b5ef", "bg": "#252E3F", "graph_bg": "#252E3F", "graph_line": "#007ACE"}
series_colors = {"1": "#92E0D3", "2": "#3AB0E3", "3": "#FF744C", "4": "#F4D44D"}

app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H1("TRANSMISSION EMULATOR", className="app__header__title"),
                        html.P(
                            "This app continually queries a simulation and displays live turbine power output given a specific wind speed and wind direction.",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                )
            ],
            className="app__header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        # input method selector
                        html.Div (
                            [
                                
                                # html.Div (
                                #     [
                                #         daq.PowerButton(
                                #             id='power_button',
                                #             label="Start Simulation",
                                #             labelPosition='bottom',
                                #             on=False,
                                #             color=app_color['primary'],
                                #             size=80,
                                            
                                            
                                #         )
                                #     ],
                                #     className='power__container'
                                    
                                # ),
                                html.Div (
                                    [
                                        html.H6(
                                            "INPUT SOURCE",
                                            className="selector__title"
                                        ),
                                        html.P(
                                            "Select a wind speed and direction source from the dropdown", className="app__p"
                                        )
                                    ],
                                ),
                                html.Div (
                                    [
                                        dcc.Dropdown(
                                            id="input_method_dd",
                                            options=[
                                               {'label': 'Manual Inputs', 'value': 'dash'},
                                               {'label': 'Flatirons Campus Current Conditions', 'value': 'nwtc'},
                                               {'label': 'ERA-5 Reanalysis Data', 'value': 'openoa'},
                                            ],
                                            value='dash',
                                            style= {'color': '#000'}
                                        )
                                    ],
                                    className="dropdown",
                                ),

                            ],
                            className="first",
                        ),
                        html.Div (
                            [
                                html.Div (
                                    [
                                        html.H3(
                                            "ERA-5 SELECTORS", className="selector__title"
                                        ),
                                        html.P(
                                            "Select a Location from the dropdown to use its wind speed and direction data", className="app__p"
                                        )
                                    ]
                                ),
                                html.Div (
                                    [
                                        dcc.Dropdown(
                                            id="locations_dd",
                                            options=[
                                               {'label': 'NREL - Flatirons Campus', 'value': 'nwtc'},
                                               {'label': 'NREL - STM Campus', 'value': 'lower_nrel'},
                                               {'label': 'Fairbanks, AK', 'value': 'fairbanks_ak'},
                                               {'label': 'Los Angeles, CA', 'value': 'los_angeles_ca'},
                                               {'label': 'Florence, SC', 'value': 'florence_sc'},
                                               {'label': 'Lincoln, NE', 'value': 'lincoln_ne'},
                                               {'label': 'Cohoes, NY', 'value': 'cohoes_ny'},
                                            ],
                                            value='lower_nrel',
                                            style= {'color': '#000'}
                                        )
                                    ],
                                    className="dropdown",
                                ),

                            ],
                            id="era-5-container",
                        ),
                        html.Div (
                            [
                                html.Div (
                                    [
                                        html.H3(
                                            "MANUAL INPUT SELECTORS", className="selector__title"
                                        ),
                                        html.P(
                                            "Slide the slider values and observe the changes on the graph", className="app__p"
                                        )
                                    ]
                                ),
                                # wind speed
                                html.Div (
                                    [
                                        html.Div(
                                            [
                                                html.H6(
                                                    "WIND SPEED (m/s)",
                                                    className="inputs__title",
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                dcc.Slider(
                                                    id="speed-slider",
                                                    min=0,
                                                    max=15,
                                                    step=0.1,
                                                    value=wind_speed_init,
                                                    updatemode="drag",
                                                    marks={
                                                        0: {"label": "0"},
                                                        3: {"label": "3"},
                                                        6: {"label": "6"},
                                                        9: {"label": "9"},                                       
                                                        12: {"label": "12"},
                                                        15: {"label": "15"},
                                                    },
                                                )
                                            ],
                                            className="slider",
                                        ),
                                        html.Div(
                                            [
                                               html.H1(id="speed-out", className="output__display")
                                            ]
                                        )
                                    ],
                                    className="first",
                                ),
                                # wind direction
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H6(
                                                    "WIND DIRECTION", className="inputs__title"
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                dcc.Slider(
                                                    id="dir-slider",
                                                    min=250,
                                                    max=290,
                                                    step=1,
                                                    value=wind_direction_init,
                                                    updatemode="drag",
                                                    marks={
                                                        250: {"label": "250"},
                                                        255: {"label": "255"},
                                                        260: {"label": "260"},
                                                        265: {"label": "265"},
                                                        270: {"label": "270"},
                                                        275: {"label": "275"},
                                                        280: {"label": "280"},
                                                        285: {"label": "285"},
                                                        290: {"label": "290"}
                                                    },
                                                )
                                            ],
                                            className="slider",
                                        ),
                                        html.Div(
                                            [
                                               html.H1(id="dir-out", className="output__display")
                                            ]
                                        )
                                    ],
                                    className="second",
                                ),
                            ],
                            id="manual-inputs-container",
                            style={'display': 'block'}
                        ),
   
                    ],
                    className="one-fourth column left__col inputs__col",
                ),
                # turbine power
                html.Div(
                    [
                     
                        html.Div (
                            [
                                # html.Div(
                                #     [html.H6("TURBINE POWER", className="graph__title")]
                                # ),
                                dcc.Graph(
                                    id="flow-image",
                                    style={'height': '50vh'}#, 'height': '90vh'}
                                ),
                                dcc.Graph(
                                    id="turbines",
                                ),
                            ],
                            className="nine columns",
                        ),
                        html.Div (
                            [
                                dcc.Interval(
                                    id="wind-speed-update",
                                    interval=int(GRAPH_INTERVAL),
                                    n_intervals=0,
                                ),
                                html.Div (
                                    [
                                        html.Div(
                                            [
                                                html.H6(
                                                    "CURRENT EMULATION CONDITIONS", className="inputs__title"
                                                )
                                            ]
                                        ),

                                    ]
                                ),
                                html.Div (
                                    [
                                        # time
                                        html.Div(
                                            [
                                                daq.LEDDisplay(
                                                    id='sim-time',
                                                    label="SIMULATION TIME",
                                                    value=0.00,
                                                    color=app_color['primary'],
                                                    backgroundColor=app_color['bg'],
                                                    size=50,
                                                ),
                                            ],
                                            className="current_condition"
                                        ),
                                        # rate
                                        html.Div(
                                            [
                                                daq.LEDDisplay(
                                                    id='time-rate',
                                                    label="SIMULATION RATE",
                                                    value=0.00,
                                                    color=app_color['primary'],
                                                    backgroundColor=app_color['bg'],
                                                    size=50
                                                ),
                                            ],
                                            className="current_condition"
                                        ), 
                                        # wind speed
                                        html.Div (
                                            [
                                                daq.LEDDisplay(
                                                    id='wind-speed-display',
                                                    label="WIND SPEED",
                                                    value=0.00,
                                                    color=app_color['primary'],
                                                    backgroundColor=app_color['bg'],
                                                    size=50
                                                )
                                            ],
                                            className="current_condition",
                                        ),
                                        # wind direction
                                        html.Div (
                                            [
                                                daq.LEDDisplay(
                                                    id='wind-dir-display',
                                                    label="WIND DIRECTION",
                                                    value="250",
                                                    color=app_color['primary'],
                                                    backgroundColor=app_color['bg'],
                                                    size=50,
                                                )
                                            ],
                                        ),

                                    ],
                                    className="results__content"
                                ),
                            ],
                            className="three columns big-top",
                        ),

                    ],
                    className="three-fourths column turbine__container",
                ),

            ],
            className="app__content",
        ),
    ],
    className="app__container",
)

# show/hide manual input sliders
@app.callback(
   Output(component_id='manual-inputs-container', component_property='style'),
   Output(component_id='era-5-container', component_property='style'),
   [Input(component_id='input_method_dd', component_property='value')])
def show_hide_element(visibility_state):
    
    manual = {'display': 'none'}
    if visibility_state == 'dash':
        manual =  {'display': 'block'}
    era5 = {'display': 'none'}
    if visibility_state == 'openoa':
        era5 = {'display': 'block'}

    return manual, era5

@app.callback(
    Output("turbines", "figure"), 
    Output("flow-image", "figure"), 
    Output('sim-time', 'value'), 
    Output('time-rate', 'value'), 
    Output("wind-speed-display", 'value'),
    Output("wind-dir-display", 'value'),
    [Input("wind-speed-update", "n_intervals")],
    [
        State(component_id='speed-slider', component_property='value'),
        State(component_id='dir-slider', component_property='value'),
        State("input_method_dd", "value"),
        # State(component_id='power_button', component_property='on'),
    ]
)
def update_turbine_power(interval, wind_speed_val, wind_dir_val, input_method):#:, power_button_val):
    """
    Update turbines graph.

    :params interval: update the graph based on an interval regardless of sliders changing
    """

    wind_speed = 0
    wind_dir = 0

    if input_method == 'dash': # If manually applied
        wind_speed = wind_speed_val
        wind_dir = wind_dir_val

    else: # Control center needs to do it
        wind_speed = -1 #Use an obviously invalid value
        wind_dir = -1 #Use an obviously invalid value

    # code used by all input methods
    logger.debug("Sending input method, wind speed and direction to control center")
    insert_data(input_method, wind_speed, wind_dir)#, power_button_val)

    logger.debug("Getting turbine data from database now")
    df_data = get_data()

    # If not in dash mode, then overwrite wind speed and wind direction now
    if not input_method == 'dash':
        logger.debug("Over-writing Wind Speed and Direction in mode: %s" % input_method)
        wind_speed = df_data[(df_data.source_system=='control_center') & (df_data.data_type=='wind_speed')].value.values[-1]
        wind_dir = df_data[(df_data.source_system=='control_center') & (df_data.data_type=='wind_direction')].value.values[-1]

    print(df_data.head())

    # Extract the turbine data and rename the columns
    df_turbine = (df_data
        [df_data.data_type=='turbine_power'] # Limit to turbine columns
        .loc[:,['sim_time_s','data_label','value']] # Take only the columns we need
        .rename({'data_label':'turbine','value':'power'}, axis='columns') # Rename columns to more useful names
        .assign(power_type = 'turbine') # Force a category type for now
    )
    
    # If big enough, drop the initial transients
    if df_turbine.sim_time_s.max() > 10:
        df_turbine = df_turbine[df_turbine.sim_time_s >= 10.]

    fig = px.area(df_turbine, 
        x="sim_time_s", 
        y="power", 
        line_group='turbine', 
        color='power_type',
        labels={
            "sim_time_s": "Time",
            "power": "Power (kW)",
            "turbine": "Turbine ID"
        },)
    fig.update_layout(template='plotly_dark', plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"], )

    # # Method 1 from png
    # im_file = sorted(os.listdir('slices'))[-1]
    # im_file = os.path.join(os.getcwd(),'slices',im_file)
    # img = io.imread(im_file)
    # fig2 = px.imshow(img)
    # fig2.update_layout(coloraxis_showscale=False)
    # fig2.update_xaxes(showticklabels=False)
    # fig2.update_yaxes(showticklabels=False)
    # fig2.update_layout(template='plotly_dark', plot_bgcolor=app_color["graph_bg"],
    #     paper_bgcolor=app_color["graph_bg"], )

    # Method 2 from data
    df_flow = pd.read_pickle('df_flow.p')
    # x, y, uh = pickle.load( open( "flow_data.p", "rb" ) )
    # fig2 = px.imshow(df_flow,aspect='equal',zmin=0,zmax=9.5, origin='lower')
    fig2 = px.imshow(df_flow,aspect='equal',zmin=2.5,zmax=9.5, origin='lower')
    fig2.update_layout(coloraxis_showscale=False)
    fig2.update_xaxes(showticklabels=False, visible=False)
    fig2.update_yaxes(showticklabels=False, visible=False)
    fig2.update_layout(template='plotly_dark', plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"], )


    # Add the turbines
    for t_idx, (x, y) in enumerate(zip(x_locs, y_locs)):

        fig2.add_shape(
            type='rect',
            x0=x, x1=x, y0=y-60, y1=y+60,
            xref='x', yref='y',
            line_color='black'
        )
        fig2.add_annotation(x=x, y=y,
            text="T%d" % t_idx,
            showarrow=True,
            xref='x', yref='y',
            arrowhead=1)

    # current sim time:
    if df_turbine.shape[0] > 0:
        sim_time = df_turbine['sim_time_s'].max()
        time_rate = np.round(df_data['time_rate_s'].values[-1],2)
    else:
        sim_time = -1
        time_rate = -1
    logger.debug("sim time: {}, time rate: {},  wind speed: {}, wind dir: {}".format(sim_time, time_rate, wind_speed, wind_dir))

    # Add some fixed formatting
    sim_time = '%04d' % sim_time
    time_rate = '%02.2f' % time_rate
    wind_speed = '%02.2f' % wind_speed
    wind_dir = '%03d' % wind_dir

    return fig, fig2, sim_time, time_rate, wind_speed, wind_dir



if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host= '0.0.0.0')