import pandas as pd
import math
import string
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import DatetimeTickFormatter, Panel, Tabs, HoverTool, CustomJS, ColumnDataSource, Slider, Dropdown, ColumnDataSource
from bokeh.layouts import widgetbox, column
from gmplot import gmplot
from bokeh.resources import CDN
from bokeh.embed import autoload_static

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

    Output: graph (HTML)'''

    output_file("average_response.html")

    temp = df.set_index('received_timestamp')
    df_time = temp.index.time

    response_time = []
    time_of_day = []

    for i,row in df.iterrows():
        if not pd.isnull(row['on_scene_timestamp']):
            diff = row['on_scene_timestamp']-row['received_timestamp']
            diff = diff.total_seconds()//60

            #within an acceptable range of values
            if diff < 60 and diff > 0:
                response_time.append(diff)

                #granularity of average
                time = df_time[i].replace(minute = df_time[i].minute - (df_time[i].minute%t))
                time = time.replace(second = 0)
                time_of_day.append(time)

    assert(len(response_time)==len(time_of_day))
    response_call_df = pd.DataFrame(data = {'response': response_time, 'call_time': time_of_day})
    #calculates average
    avg_response_time = response_call_df.groupby(['call_time'])['response'].mean()

    #generates column data
    data = {'time':avg_response_time.index,
            'response':avg_response_time}
    # print(data['time'])
    source = ColumnDataSource(data=data)

    #plots averages
    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,save"

    p = figure(plot_width = 700, plot_height = 350, title = "Average Response Time VS Call Time", tools = TOOLS)
    p.line(x = 'time', y = 'response', source = source)
    p.xaxis.formatter=DatetimeTickFormatter()
    p.xaxis.major_label_orientation = math.pi/4
    p.grid.grid_line_alpha=0.3

    p.xaxis.axis_label = 'Time of Day'
    p.yaxis.axis_label = 'Average Response'

    hover = p.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    hover.tooltips = [
        ("Time", "@time{%T}"),
        ("Dispatch Response Time", "@response")
    ]
    hover.formatters = {'time':'datetime'}

    show(p)

response_to_call(df)

#---------------------CALL LOCATION HEAT MAP-----------------------------------#
def calls_per_area(df):
    '''This function provides a heat map of the number of calls through the
    San Francisco area.

    Input: df (pd.DataFrame)

    Output: heatmap (html)'''
    gmap = gmplot.GoogleMapPlotter(37.766956, -122.438481, 13)
    
    latlng_list = []
    for i, row in df.iterrows():
        latlng_list.append((row['latitude'],row['longitude']))

    heat_lats, heat_lngs = zip(*latlng_list)
    gmap.heatmap(heat_lats, heat_lngs)
    gmap.draw("heatmap.html")

calls_per_area(df)
    

#---------------------AMBULANCE TRANSPORT VS CALL TIME-------------------------#
def ambulance_response(df):
    '''This function graphs the transport time of an ambulance against the time
    of day the call was made.

    Input: df (pd.DataFrame)

    Output: graph (HTML)
            times (pd.Series)
            average ambulance response per time (pd.Series)'''

    output_file("ambulance.html")

    temp = df.set_index('received_timestamp')
    df_time = temp.index.time

    ambulance_time = []
    time_of_day = []

    for i,row in df.iterrows():
        if not pd.isnull(row['hospital_timestamp']):
            diff = row['hospital_timestamp']-row['received_timestamp']
            diff = diff.total_seconds()//60

            #within an acceptable range of values
            if diff < 60 and diff > 0:
                ambulance_time.append(diff)

                #granularity of average
                time = df_time[i].replace(minute = df_time[i].minute - (df_time[i].minute%10))
                time = time.replace(second = 0)
                time_of_day.append(time)

    assert(len(ambulance_time)==len(time_of_day))
    response_df = pd.DataFrame(data = {'transport': ambulance_time, 'call_time': time_of_day})
    #calculates average
    avg_response_time = response_df.groupby(['call_time'])['transport'].mean()

    #generates column data
    data = {'time':avg_response_time.index,
            'response':avg_response_time}
    source = ColumnDataSource(data=data)

    #plots averages
    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,save"

    p = figure(plot_width = 700, plot_height = 350, title = "Average Ambulance Transport Time VS Call Time", tools = TOOLS)
    p.line(x = 'time', y = 'response', source = source)
    p.xaxis.formatter=DatetimeTickFormatter()
    p.xaxis.major_label_orientation = math.pi/4
    p.grid.grid_line_alpha=0.3

    p.xaxis.axis_label = 'Time of Day'
    p.yaxis.axis_label = 'Average Ambulance Transport Time'

    hover = p.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    hover.tooltips = [
        ("Time", "@time{%T}"),
        ("Ambulance Response Time", "@response")
    ]
    hover.formatters = {'time':'datetime'}

    show(p)

ambulance_response(df)

#---------------------MOST LIKELY DISPATCH-------------------------------------#
def dispatch_required(df):
    '''This function predicts the unit_type most likely to respond to a call
    in a certain location/time.

    Input: df (pd.DataFrame)

    Output: unit_type (string)'''
    pass


#---------------------AREA VS DISPATCH TIME------------------------------------#
def longest_dispatch(df):
    '''This function answers the query of which area takes the longest dispatch
    response time.

    Input: df (pd.DataFrame)

    Output: (zipcode, time) tuple of int set and int'''
    
    dispatch_dict = dict()
    for i,row in df.iterrows():
        if not pd.isnull(row['on_scene_timestamp']):
            dispatch = row['on_scene_timestamp']-row['received_timestamp']
            dispatch_min = dispatch.total_seconds()//60
            if row['zipcode_of_incident'] not in dispatch_dict:
                dispatch_dict[row['zipcode_of_incident']] = [dispatch_min]
            else:
                dispatch_dict[row['zipcode_of_incident']] += [dispatch_min]

    max_time = 0
    max_zip = set()
    for zipcode in dispatch_dict:
        average = sum(dispatch_dict[zipcode])/len(dispatch_dict[zipcode])
        if average > max_time:
            max_time = average
            max_zip.clear()
            max_zip.add(zipcode)
        elif average == max_time:
            max_zip.add(zipcode)

    return (max_zip, max_time) 

print(longest_dispatch(df))

