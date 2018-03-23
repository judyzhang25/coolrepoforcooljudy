import pandas as pd
import math
import string
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import DatetimeTickFormatter
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Slider

#---------------------LOADING CSV INTO PANDAS DATAFRAME------------------------#
def load_data(fname):
    df = pd.read_csv(fname)

    #dropping unused columns
    df = df.drop(['watch_date', 'entry_timestamp', 'dispatch_timestamp', 'response_timestamp', 'city', 'unit_sequence_in_call_dispatch'],1)
    
    #ensuring proper types
    df['call_date'] = pd.to_datetime(df['call_date'])
    df['received_timestamp'] = pd.to_datetime(df['received_timestamp'])
    df['on_scene_timestamp'] = pd.to_datetime(df['on_scene_timestamp'])
    df['transport_timestamp'] = pd.to_datetime(df['transport_timestamp'])
    df['hospital_timestamp'] = pd.to_datetime(df['hospital_timestamp'])
    df['available_timestamp'] = pd.to_datetime(df['available_timestamp'])
    df['final_priority'] = df['final_priority'].astype('object')
    df['supervisor_district'] = df['supervisor_district'].astype('object')
    df['neighborhood_district'] = df['neighborhood_district'].astype('object')

    #blank spaces are filled with NaN
    return df

#testing data
df = load_data('sfpd_dispatch_data_subset.csv')
#verifying number of columns
assert(30 == df.shape[1])
# print(df.dtypes)
# print(df.head())

#---------------------AVG RESPONSE TIME VS CALL TIME---------------------------#
def response_to_call(df, t=5):
    '''This function graphs the average dispatch response time against the time 
    of day the call was made.

    Input: df (pd.DataFrame)
           t  (int; the granularity of each time period in min for which an 
               average response time is calculated)

    Output: graph'''

    temp = df.set_index('received_timestamp')
    df_time = temp.index.time

    response_time = []
    time_of_day = []

    for i,row in df.iterrows():
        if not pd.isnull(row['on_scene_timestamp']):
            diff = row['on_scene_timestamp']-row['received_timestamp']
            diff = diff.total_seconds()//60
            if diff < 60 and diff > 0:
                response_time.append(diff)
                time = df_time[i].replace(minute = df_time[i].minute - (df_time[i].minute%t))
                time = time.replace(second = 0)
                time_of_day.append(time)

    assert(len(response_time)==len(time_of_day))
    response_call_df = pd.DataFrame(data = {'response': response_time, 'call_time': time_of_day})
    avg_response_time = response_call_df.groupby(['call_time'])['response'].mean()

    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,save"

    p = figure(plot_width = 800, plot_height = 400, title = "Average Response Time VS Call Time", tools = TOOLS)
    p.line(avg_response_time.index, avg_response_time)
    p.xaxis.formatter=DatetimeTickFormatter()
    p.xaxis.major_label_orientation = math.pi/4
    p.grid.grid_line_alpha=0.3

    p.xaxis.axis_label = 'Time of Day'
    p.yaxis.axis_label = 'Average Response'

    slider = Slider(start=0, end=10, value=1, step=.1, title="Stuff")

    show(p)
    show(slider)
    return (avg_response_time.index, avg_response_time)

response_to_call(df)

#---------------------ZIPCODE VS CALL TYPE-------------------------------------#
def calls_per_area(df, zipcode, call='all'):
    '''This function provides the data associating the number of calls of a
    particular type with a certain area. If the call type is not specified,
    then it provides the total number of dispatch calls per area.

    Input: df (pd.DataFrame)
           zipcode (int)
           call (string)

    Output: result (pd.DataFrame)'''
    pass

#---------------------AMBULANCE TRANSPORT VS CALL TIME-------------------------#
def ambulance_response(df):
    '''This function graphs the transport time of an ambulance against the time
    of day the call was made.

    Input: df (pd.DataFrame)

    Output: graph'''
    pass

#---------------------MOST LIKELY DISPATCH-------------------------------------#
def dispatch_required(df, address, time):
    '''This function predicts the unit_type most likely to respond to a call
    in a certain location/time.

    Input: df (pd.DataFrame)
           address (string)
           time (datetime)

    Output: unit_type (string)'''
    pass


#---------------------AREA VS DISPATCH TIME------------------------------------#
def longest_dispatch(df):
    '''This function answers the query of which area takes the longest dispatch
    response time.

    Input: df (pd.DataFrame)

    Output: (area, result) tuple of string and pd.DataFrame'''
    pass

