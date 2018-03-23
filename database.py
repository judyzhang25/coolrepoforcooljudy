import pandas as pd
import math
import string
import numpy as np
from bokeh.plotting import figure, output_file, show

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
print(df.dtypes)
print(df.head())

#---------------------RESPONSE TIME VS CALL TIME-------------------------------#
def response_to_call(df):
    '''This function graphs the dispatch response time against the time of day
    the call was made.

    Input: df (pd.DataFrame)

    Output: graph'''
    pass

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

