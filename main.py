import pandas as pd
import math
from bokeh.plotting import figure, output_file, show
from bokeh.models import DatetimeTickFormatter, Panel, Tabs, HoverTool, CustomJS, ColumnDataSource, Panel, Tabs, DataTable, DateFormatter, TableColumn
from bokeh.layouts import widgetbox, column
from gmplot import gmplot
from bokeh.resources import CDN
from bokeh.embed import autoload_static
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyCwQDcVpWzxDW7lnWqJjivaGXO3YBo2-IU"

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
def response_to_call(df, t=30):
    '''This function graphs the average dispatch response time against the time 
    of day the call was made.

    Input: df (pd.DataFrame)
           t  (int; the granularity of each time period in min for which an 
               average response time is calculated)

    Output: graph (HTML)'''

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

    return p

def tabbed_call(df):
    output_file("response_tabs.html")
    tab1 = Panel(child=response_to_call(df, 15), title = "Quarter Hour")
    tab2 = Panel(child=response_to_call(df), title = "Half Hour")
    tab3 = Panel(child=response_to_call(df, 60), title = "Hour")

    tabs = Tabs(tabs=[tab1,tab2,tab3])
    show(tabs)

#tabbed_call(df)

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

#calls_per_area(df)
    

#---------------------AMBULANCE TRANSPORT VS CALL TIME-------------------------#
def ambulance_response(df, t=30):
    '''This function graphs the transport time of an ambulance against the time
    of day the call was made.

    Input: df (pd.DataFrame)
           t  (int; the granularity of each time period in min for which an 
               average response time is calculated)

    Output: graph (HTML)'''


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
                time = df_time[i].replace(minute = df_time[i].minute - (df_time[i].minute%t))
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

    return p

def tabbed_am(df):
    output_file("ambulance_tabs.html")
    tab1 = Panel(child=ambulance_response(df, 15), title = "Quarter Hour")
    tab2 = Panel(child=ambulance_response(df), title = "Half Hour")
    tab3 = Panel(child=ambulance_response(df, 60), title = "Hour")

    tabs = Tabs(tabs=[tab1,tab2,tab3])
    show(tabs)

#tabbed_am(df)



#---------------------AREA VS DISPATCH TIME------------------------------------#
def longest_dispatch(df):
    '''This function answers the query of which area takes the longest dispatch
    response time.

    Input: df (pd.DataFrame)

    Output: (zipcode, time) tuple of int set and int'''
    output_file("area_times.html")

    dispatch_dict = dict()
    #creates dictionary of dispatch times per zip
    for i,row in df.iterrows():
        if not pd.isnull(row['on_scene_timestamp']):
            dispatch = row['on_scene_timestamp']-row['received_timestamp']
            dispatch_min = dispatch.total_seconds()//60
            if dispatch_min > 0 and dispatch_min < 120:
                if row['zipcode_of_incident'] not in dispatch_dict:
                    dispatch_dict[row['zipcode_of_incident']] = [dispatch_min]
                else:
                    dispatch_dict[row['zipcode_of_incident']] += [dispatch_min]

    #finds zip and longest dispatch time
    max_time = 0
    max_zip = set()
    zips = []
    times = []
    for zipcode in dispatch_dict:
        zips.append(zipcode)
        average = sum(dispatch_dict[zipcode])/len(dispatch_dict[zipcode])
        times.append(average)
        if average > max_time:
            max_time = average
            max_zip.clear()
            max_zip.add(zipcode)
        elif average == max_time:
            max_zip.add(zipcode)

    data = dict(zipcodes=zips,averages=times)
    source = ColumnDataSource(data=data)

    columns = [
            TableColumn(field="zipcodes", title="Zipcode"),
            TableColumn(field="averages", title="Average Dispatch Time"),
        ]
    data_table = DataTable(source=source, columns=columns, width=700, height=300, sortable=True)

    show(widgetbox(data_table))

    return (max_zip, max_time) 

def most_common_call(df, zipcode):
    #finds the most common unit dispatch for a zipcode
    print(zipcode)
    call_dict = dict()
    for i,row in df.iterrows():
        if not pd.isnull(row['unit_type']) and row['zipcode_of_incident'] == zipcode:
            call_dict[row['unit_type']] = call_dict.get(row['unit_type'],1) + 1
    print(call_dict)

    max_count = 0
    most_common = []
    for key in call_dict:
        if call_dict[key] > max_count:
            most_common = [key]
            max_count = call_dict[key]
        elif call_dict[key] == max_count:
            most_common.append(key)

    return most_common

# values = longest_dispatch(df)
# print(values)
# print(most_common_call(df,list(values[0])[0]))

