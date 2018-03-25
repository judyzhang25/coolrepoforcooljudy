from bokeh.layouts import widgetbox, row
from bokeh.models import CustomJS, ColumnDataSource, Slider, Dropdown, Paragraph
from bokeh.plotting import figure, output_file, show
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

Output: text, dropdown, output (bokeh widgets and resulting string)'''
output_file("dispatch_required.html")

source = ColumnDataSource(
    {'call_time':df['received_timestamp'],
     'unit':df['unit_type'],
     'zipcode':df['zipcode_of_incident'],
     'result':""})

callback = CustomJS(args=dict(source=source), code="""
        // get data source from Callback args
        var data = source.data;
        var hour = time.value;
        var zip = zipcode.value;
        var times = data['call_time']
        var units = data['unit']

        for (i = 0; i < x.length; i++) {
            y[i] = B + A*Math.sin(k*x[i]+phi);
        }

        /// calculate Rect attributes
        var width = geometry['x1'] - geometry['x0'];
        var height = geometry['y1'] - geometry['y0'];
        var x = geometry['x0'] + width/2;
        var y = geometry['y0'] + height/2;

        /// update data source with new Rect attributes
        data['x'].push(x);
        data['y'].push(y);
        data['width'].push(width);
        data['height'].push(height);

        // emit update of data source
        source.change.emit();
    """)

#dispatch
def dispatch_required(df, zipcode, est_time):
    #counts the frequency of unit calls per hour and zipcode given
    dispatch_dict = dict()
    for i,row in df.iterrows():
        if row['zipcode_of_incident'] == zipcode and row['received_timestamp'].hour == est_time:
             dispatch_dict[row['unit_type']] = dispatch_dict.get(row['unit_type'],1) + 1

    #finds most common dispatch at time
    max_count = 0
    most_common = ""
    for key in dispatch_dict:
        if dispatch_dict[key] > max_count:
            most_common = key
            max_count = dispatch_dict[key]
        elif dispatch_dict[key] == max_count:
            most_common += ", " + key

    return most_common

#dropdown zipcode input
zip_menu = [("94102",94102),
            ("94103",94103),
            ("94104",94104),
            ("94105",94105),
            ("94107",94107),
            ("94108",94108),
            ("94109",94109),
            ("94110",94110),
            ("94111",94111),
            ("94112",94112),
            ("94114",94114),
            ("94115",94115),
            ("94116",94116),
            ("94117",94117),
            ("94118",94118),
            ("94121",94121),
            ("94122",94122),
            ("94123",94123),
            ("94124",94124),
            ("94127",94127),
            ("94129",94129),
            ("94130",94130),
            ("94131",94131),
            ("94132",94132),
            ("94133",94133),
            ("94134",94134),
            ("94158",94158)]
zipcode = Dropdown(label="Zipcode", button_type="warning", menu=zip_menu, callback=callback)
callback.args["zipcode"] = zipcode

#dropdown time input
menu = [("12:00 AM", 0),
        ("1:00 AM", 1),
        ("2:00 AM", 2),
        ("3:00 AM", 3),
        ("4:00 AM", 4),
        ("5:00 AM", 5),
        ("6:00 AM", 6),
        ("7:00 AM", 7),
        ("8:00 AM", 8),
        ("9:00 AM", 9),
        ("10:00 AM", 10),
        ("11:00 AM", 11),
        ("12:00 PM", 12),
        ("1:00 PM", 13),
        ("2:00 PM", 14),
        ("3:00 PM", 15),
        ("4:00 PM", 16),
        ("5:00 PM", 17),
        ("6:00 PM", 18),
        ("7:00 PM", 19),
        ("8:00 PM", 20),
        ("9:00 PM", 21),
        ("10:00 PM", 22),
        ("11:00 PM", 23)
        ]
time = Dropdown(label="Time of Day", button_type="warning", menu=menu, callback=callback)
callback.args["time"] = time

p = Paragraph(text="@result", width=200, height=100, callback=callback)

layout = row(
widgetbox(text_input),
widgetbox(time),
widgetbox(p)
)
show(layout)




