# %%
"""
* USA Counties map: https://commons.wikimedia.org/wiki/File:USA_Counties_with_FIPS_and_names.svg
"""

# %%
import pandas as pd
import numpy as np
import datetime as dt
from math import sin, cos, sqrt, atan2, radians

from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.us_counties import data as counties # needed to run bokeh.sampledata.download()
from bokeh.sampledata.us_states import data as states

# %%
"""
# Columns
 
* FIPS: Federal Information Processing Standards code that uniquely identifies counties in the US
* Admin2: County name (US)
* Lat and Long_: geographical centroids
* Confirmed: includes presumed positive and probable cases, per CDC from April 14
"""

# %%
df = pd.read_csv("data/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/05-13-2020.csv")
# remove all non-US rows
df = df.loc[df['Country_Region'] == 'US']
df

# %%
"""
# Initialize everything related to dates and times
"""

# %%
def csv_from_date(date):
    return str(date.month).zfill(2) + '-' + str(date.day).zfill(2) + '-' + str(date.year) + '.csv'

# %%
now = dt.datetime.now()
today = dt.date.today() # 2020-05-14
EARLIEST = dt.date(2020, 1, 22)
LATEST = dt.date(2020, 5, 19)

# create date range
date_range = list()
date_range.append(EARLIEST)
step = dt.timedelta(days=1)
next_date = EARLIEST + step 
while next_date <= LATEST:
    date_range.append(next_date)
    next_date += step

print(today.year)
print(today.month)
print(str(today.month).zfill(2))
print(today.day)
print(today)
print(str(today.day).zfill(2))
print(csv_from_date(today))
print(csv_from_date(EARLIEST))
print(date_range)

# %%
# build dict of dataframes from all the dataframes/csv's for the date range
dfs = dict()
for d in date_range:
    fp = 'data/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/' + csv_from_date(d)
    dfs[str(d)] = pd.read_csv(fp)

dfs

# %%
"""
## Silver Bow County

* FIPS: 30093
* Lat: 45.900189
* Long: -112.662009
"""

# %%
df.loc[df['FIPS'] == 30093.0]

# %%
"""
## Gallatin County

* FIPS: 30031
* Lat: 45.544861
* Long: -111.169257
"""

# %%
df.loc[df['FIPS'] == 30031.0]

# %%
# https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def distance_km(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def distance_miles(lat1, lon1, lat2, lon2):
    return 0.621371 * distance_km(lat1, lon1, lat2, lon2)

# %%
# example: calculate distance between Silver Bow and Gallatin County in miles

distance_miles(45.900189, -112.662009, 45.544861, -111.169257)

# %%
def get_location():
    while True:
        county = input("Enter the name of the target county: ")
        # is this a valid entry?
        if county in list(df['Admin2']):
            break
        else:
            print("invalid county name")

    return county

# %%
def get_radius():
    # get the radius for the counties to include
    radius = int(input("Enter the radius (in miles) for nearby counties to include: "))
    return radius

# %%
def get_county_coord(county):
    row = df.loc[df['Admin2'] == county]
    return row['Lat'].values[0], row['Long_'].values[0]

# %%
def get_fips(county):
    row = df.loc[df['Admin2'] == county]
    return row['FIPS'].values[0]

# %%
def rad_counties(lat, lon, rad):
    counties = list()
    for index, row in df.iterrows():
        if distance_miles(lat, lon, row['Lat'], row['Long_']) <= rad:
            counties.append(row['FIPS'])
    return counties # returns the FIPS code of the counties

# %%
user_loc = get_location()
user_rad = get_radius()
user_coord = get_county_coord(user_loc)

print(user_loc)
print(user_rad)
print(user_coord)
print(rad_counties(user_coord[0], user_coord[1], user_rad))

# %%
date_list = list(dfs.keys())
date_list.reverse()
last_date = date_list[0]
dfs[last_date].loc[dfs[last_date]['FIPS'] == 30093]

# %%
def last_confirmed(fips):
    # walk backward the dates until the number of confirmed cases decreases
    date_list = list(dfs.keys())
    date_list.reverse()
    last_date = date_list[0]
    last_row = dfs[last_date].loc[dfs[last_date]['FIPS'] == fips]
    # TODO: if len(last_row) is 0, return NaN
    #last_row = dfs[last_date].values.loc[df['FIPS'] == fips]
    last_confirmed_num = last_row['Confirmed'].values[0]
    for i in date_list:
        #print(i)
        row = dfs[i].loc[dfs[i]['FIPS'] == fips]
        if len(row) < 1:
            return(last_date)
        if row['Confirmed'].values[0] < last_confirmed_num:
            return i
        last_date = i
        last_row = row
        last_confirmed_num = row['Confirmed'].values[0]

# %%
# build dict of counties and their last_confirmed
counties = rad_counties(user_coord[0], user_coord[1], user_rad)
county_dat = dict()
for c in counties:
    county_dat[c] = last_confirmed(int(c))

print(county_dat)

# %%
"""
## Build the Map
"""

# %%
# http://docs.bokeh.org/en/0.11.0/docs/gallery/choropleth.html

#del states["HI"]
#del states["AK"]

EXCLUDED = ("ak", "hi", "pr", "gu", "vi", "mp", "as")

mt_state = {'MT': states['MT']}

state_xs = [states[code]["lons"] for code in mt_state]
state_ys = [states[code]["lats"] for code in mt_state]

county_xs=[counties[code]["lons"] for code in counties if counties[code]["state"] in ('mt')]
county_ys=[counties[code]["lats"] for code in counties if counties[code]["state"] in ('mt')]

p = figure(title="Days since last confirmed Covid-19 case", toolbar_location="left",
           plot_width=1100, plot_height=700)
p.patches(county_xs, county_ys,
          fill_color="white", fill_alpha=0.7,
          line_color="blue", line_width=0.5)
p.patches(state_xs, state_ys, fill_alpha=0.0,
          line_color="#884444", line_width=2, line_alpha=0.3)
show(p)

# %%
print({'MT': states['MT']})

# %%
