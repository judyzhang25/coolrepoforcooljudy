import csv
import sqlite3
import pandas
import math
import string
import numpy as np
#from bokeh.plotting import figure, output_file, show

#---------------------LOADING CSV------------------------#
def load_dispatch_data(conn, filepath):
	"""loads data from file as tables into an in-memory SQLITE database
	Input: conn (sqlite3.connection), filepath (str)
	Output: None"""

	c = conn.cursor()
	c.execute('''CREATE TABLE dispatch()''')


#connect to an in memory database
conn = sqlite3.connect(":memory:")
conn.text_factor = str

load_dispatch_data(conn, 'sfpd_dispatch_data_subset.csv')
cursor = conn.cursor()


