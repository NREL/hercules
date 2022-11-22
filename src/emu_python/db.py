import pathlib
import sqlite3
import datetime
import pandas as pd

control_center_database_filename = pathlib.Path(__file__).parent / 'control_center.db'
front_end_database_filename = pathlib.Path(__file__).parent / 'front_end.db'

num_turbines = 4

def get_turbine_locs():

    with sqlite3.connect(str(control_center_database_filename)) as con:
            statement = f'SELECT * from data_table where data_type = "x_loc" order by data_label;'
            df = pd.read_sql_query(statement, con)
            x_locs = df['value'].values

            statement = f'SELECT * from data_table where data_type = "y_loc" order by data_label;'
            df = pd.read_sql_query(statement, con)
            y_locs = df['value'].values



    return x_locs, y_locs


def get_data(num_records=600):
    """
    Query wind data rows 
    :params num_records: number of records to retrieve, defaults to 600 (10 mins)
    num_records will be multiplied by number of turbines to get full data
    :returns: pandas dataframe object
    """

    # multiply by records by num turbines
    num_recs = num_records * num_turbines

    with sqlite3.connect(str(control_center_database_filename)) as con:
        statement = f'SELECT * from data_table where sim_time_s > (SELECT MAX(sim_time_s)-"{num_recs}" from data_table) order by sim_time_s;'
        df = pd.read_sql_query(statement, con)


    return df

def insert_data(input_method, wind_speed, wind_direction, solar_it, storage_radio):#, power_button_val):

    insertQuery = "INSERT INTO front_end_table VALUES (?, ?, ?, ?);"

    # Connect to the database
    with sqlite3.connect(front_end_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
        # con = sqlite3.connect(front_end_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor() # Get the cursor

        # get the current datetime and store it in a variable
        currentDateTime = datetime.datetime.now()

        # Post the input method, wind speed, wind directon to front end database
        # tuple_to_add = (currentDateTime, 'power_button','power_button', power_button_val)
        # cur.execute(insertQuery, tuple_to_add)
        tuple_to_add = (currentDateTime, 'input_method',input_method, 0)
        cur.execute(insertQuery, tuple_to_add)
        tuple_to_add = (currentDateTime, 'wind_speed','wind_speed', wind_speed)
        cur.execute(insertQuery, tuple_to_add)
        tuple_to_add = (currentDateTime, 'wind_direction','wind_direction', wind_direction)
        cur.execute(insertQuery, tuple_to_add)
        tuple_to_add = (currentDateTime, 'solar_it','solar_it', solar_it)
        cur.execute(insertQuery, tuple_to_add)
        tuple_to_add = (currentDateTime, 'storage_radio','storage_radio', storage_radio)
        cur.execute(insertQuery, tuple_to_add)
    