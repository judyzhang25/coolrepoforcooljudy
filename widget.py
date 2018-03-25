from bokeh.layouts import widgetbox, row
from bokeh.models import CustomJS, ColumnDataSource, Slider, Dropdown, TextInput, Div, Paragraph
from bokeh.plotting import figure, output_file, show
from bokeh.io import curdoc

import pandas as pd

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

df = load_data('sfpd_dispatch_data_subset.csv')

#---------------------MOST LIKELY DISPATCH-------------------------------------#
'''This function predicts the unit_type most likely to respond to a call
in a certain location/time.

Input: df (pd.DataFrame)

Output: zipcode dropdown, time of day dropdown, output unit (bokeh widgets and 
resulting string)'''
output_file("dispatch_required.html")
data = {'call_time': df['received_timestamp'], 'unit': df['unit_type'], 'zipcode':df['zipcode_of_incident']}
result = "MEDIC"
source = ColumnDataSource(data=data)

#initializing variables
t=0
z=94102

# callback = CustomJS(args=dict(source=source), code="""
#         // get data source from Callback args
#         var data = source.data;
#         var hour = time.value;
#         var zip = zip.value;
#         var times = data['call_time'];
#         var units = data['unit'];
#         var zipcodes = data['zipcode'];

#         var d = {};

#         for (i = 0; i < times.length; i++) {
#             if times[i].getHours() === hour && zipcodes[i] === zip{
#                 if unit[i] in d{
#                     var d[unit[i]] = d[unit[i]] + 1;
#                 } else {
#                     var d[unit[i]] = 1;
#                 }
#             }
#         }

#         var count = 0;

#         for (var key in d){
#             if d[key]>count{
#                 var data['result'] = key;
#                 var count = d[key];
#             }
#         }

#         source.change.emit();
#     """)

#dispatch
def dispatch_required(source=source):
    #counts the frequency of unit calls per hour and zipcode given
    datum= source.data
    zipcodes = datum['zipcode']
    times = datum['call_time']
    units = datum['unit']

    dispatch_dict = dict()
    for i,row in df.iterrows():
        if zipcodes[i] == z and times[i].hour == t:
             dispatch_dict[units[i]] = dispatch_dict.get(units[i],1) + 1

    #finds most common dispatch at time
    max_count = 0
    most_common = ""
    for key in dispatch_dict:
        if dispatch_dict[key] > max_count:
            most_common = key
            max_count = dispatch_dict[key]
        elif dispatch_dict[key] == max_count:
            most_common += ", " + key

    result = most_common
    source.trigger('change')

#dropdown zipcode input
zip_menu = [("94102","94102"),
            ("94103","94103"),
            ("94104","94104"),
            ("94105","94105"),
            ("94107","94107"),
            ("94108","94108"),
            ("94109","94109"),
            ("94110","94110"),
            ("94111","94111"),
            ("94112","94112"),
            ("94114","94114"),
            ("94115","94115"),
            ("94116","94116"),
            ("94117","94117"),
            ("94118","94118"),
            ("94121","94121"),
            ("94122","94122"),
            ("94123","94123"),
            ("94124","94124"),
            ("94127","94127"),
            ("94129","94129"),
            ("94130","94130"),
            ("94131","94131"),
            ("94132","94132"),
            ("94133","94133"),
            ("94134","94134"),
            ("94158","94158")]
zipdrop = Dropdown(label="Zipcode", button_type="warning", menu=zip_menu, callback=CustomJS.from_py_func(dispatch_required))
z = zipdrop.value


#dropdown time input
menu = [("12:00 AM", "0"),
        ("1:00 AM", "1"),
        ("2:00 AM", "2"),
        ("3:00 AM", "3"),
        ("4:00 AM", "4"),
        ("5:00 AM", "5"),
        ("6:00 AM", "6"),
        ("7:00 AM", "7"),
        ("8:00 AM", "8"),
        ("9:00 AM", "9"),
        ("10:00 AM", "10"),
        ("11:00 AM", "11"),
        ("12:00 PM", "12"),
        ("1:00 PM", "13"),
        ("2:00 PM", "14"),
        ("3:00 PM", "15"),
        ("4:00 PM", "16"),
        ("5:00 PM", "17"),
        ("6:00 PM", "18"),
        ("7:00 PM", "19"),
        ("8:00 PM", "20"),
        ("9:00 PM", "21"),
        ("10:00 PM", "22"),
        ("11:00 PM", "23")
        ]
timedrop = Dropdown(label="Time of Day", button_type="warning", menu=menu, callback=CustomJS.from_py_func(dispatch_required))
t = timedrop.value


p = Paragraph(text="Unit:" + result, width=200, height=100)

layout = row(
widgetbox(zipdrop),
widgetbox(timedrop),
widgetbox(p)
)
show(layout)




