
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import datetime as dt
from math import sin, cos, sqrt, atan2, radians


# # Columns
# 
# * FIPS: Federal Information Processing Standards code that uniquely identifies counties in the US
# * Admin2: County name (US)
# * Lat and Long_: geographical centroids
# * Confirmed: includes presumed positive and probable cases, per CDC from April 14

# In[ ]:


df = pd.read_csv("data/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/05-13-2020.csv")
# remove all non-US rows
df = df.loc[df['Country_Region'] == 'US']
df


# # Initialize everything related to dates and times

# In[ ]:


def csv_from_date(date):
    return str(date.month).zfill(2) + '-' + str(date.day).zfill(2) + '-' + str(date.year) + '.csv'


# In[ ]:


now = dt.datetime.now()
today = dt.date.today() # 2020-05-14
EARLIEST = dt.date(2020, 1, 22)
LATEST = dt.date(2020, 5, 13)

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


# In[ ]:


# build dict of dataframes from all the dataframes/csv's for the date range
dfs = dict()
for d in date_range:
    fp = 'data/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/' + csv_from_date(d)
    dfs[str(d)] = pd.read_csv(fp)

dfs


# In[ ]:


for x in dfs:
    print(x)


# ## Silver Bow County
# 
# * FIPS: 30093
# * Lat: 45.900189
# * Long: -112.662009

# In[ ]:


df.loc[df['FIPS'] == 30093.0]


# ## Gallatin County
# 
# * FIPS: 30031
# * Lat: 45.544861
# * Long: -111.169257

# In[ ]:


df.loc[df['FIPS'] == 30031.0]


# In[ ]:


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


# In[ ]:


# example: calculate distance between Silver Bow and Gallatin County in miles

distance_miles(45.900189, -112.662009, 45.544861, -111.169257)


# In[ ]:


def get_location():
    while True:
        county = input("Enter the name of the target county: ")
        # is this a valid entry?
        if county in list(df['Admin2']):
            break
        else:
            print("invalid county name")

    return county


# In[ ]:


def get_radius():
    # get the radius for the counties to include
    radius = int(input("Enter the radius (in miles) for nearby counties to include: "))
    return radius


# In[ ]:


def get_county_coord(county):
    row = df.loc[df['Admin2'] == county]
    return row['Lat'].values[0], row['Long_'].values[0]


# In[ ]:


def get_fips(county):
    row = df.loc[df['Admin2'] == county]
    return row['FIPS'].values[0]


# In[ ]:


def rad_counties(lat, lon, rad):
    counties = list()
    for index, row in df.iterrows():
        if distance_miles(lat, lon, row['Lat'], row['Long_']) <= rad:
            counties.append(row['FIPS'])
    return counties # returns the FIPS code of the counties


# In[ ]:


user_loc = get_location()
user_rad = get_radius()
user_coord = get_county_coord(user_loc)

print(user_loc)
print(user_rad)
print(user_coord)
print(rad_counties(user_coord[0], user_coord[1], user_rad))


# In[ ]:


date_list = list(dfs.keys())
date_list.reverse()
last_date = date_list[0]
dfs[last_date].loc[dfs[last_date]['FIPS'] == 30093]


# In[ ]:


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
        print(i)
        row = dfs[i].loc[dfs[i]['FIPS'] == fips]
        if len(row) < 1:
            return(last_date)
        if row['Confirmed'].values[0] < last_confirmed_num:
            return i
        last_date = i
        last_row = row
        last_confirmed_num = row['Confirmed'].values[0]
        
last_confirmed(30001)


# In[ ]:


# build dict of counties and their last_confirmed
counties = rad_counties(user_coord[0], user_coord[1], user_rad)
county_dat = dict()
for c in counties:
    print(c)
    #county_dat[c] = last_confirmed(int(c))

last_date = str(dt.date(2020, 4, 3))
last_row = dfs[last_date].loc[dfs[last_date]['FIPS'] == 30001]
#print(last_row)
#print(last_row['Confirmed'].values[0])
print("number of rows: " + str(len(last_row)))

