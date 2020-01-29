#!/usr/bin/env python
# coding: utf-8

# <h1>Install necessary libraries</h1>

# In[1]:


get_ipython().system('pip install geocoder')
get_ipython().system('pip install folium')
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import types
from botocore.client import Config
import ibm_boto3
import folium
from geopy.geocoders import Nominatim
from sklearn.cluster import KMeans
import matplotlib.cm as cm
import matplotlib.colors as colors


# <h1>Scrape the Web Page for data</h1>

# In[2]:


website_url = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup = BeautifulSoup(website_url,'lxml')


# In[3]:


My_table = soup.find('table',{'class':'wikitable sortable'})
content = My_table.findAll('td')  


# In[4]:


list1 = []
list2 = []
list3 = []
for i in range(0,len(content)):
    if((i+1) % 3 == 0):
        list3.append(content[i].getText('Title'));
    elif((i) % 3 == 0):
        list1.append(content[i].getText('Title'));
    else:
        list2.append(content[i].getText('Title'));    


# In[5]:


newList1 = []
newList2 = []
newList3 = []
for i in range(0, len(list2)):
    if(list2[i] != 'Not assigned'):
        newList1.append(list1[i])
        newList2.append(list2[i])
        temp = list3[i].replace('\n','')
        newList3.append(temp)

for i in range(0, len(newList3)):
    if(newList3[i] == 'Not assigned'):
        newList3[i] = newList2[i]     


# In[6]:


df1 = pd.DataFrame(newList1, columns =['PostalCode'])
df1['Borough'] = newList2
df1['Neighborhood'] = newList3
df = df1.groupby(['PostalCode','Borough'],sort=False).agg(lambda x: ','.join(x)).reset_index()

df.head()


# In[7]:


df.shape


# <h1>Use the CSV File to map the latitude and longitude for various regions</h1>

# In[8]:


def __iter__(self): return 0

# @hidden_cell
# The following code accesses a file in your IBM Cloud Object Storage. It includes your credentials.
# You might want to remove those credentials before you share the notebook.
client_c3fe26565e19406dad94b51edbfa2846 = ibm_boto3.client(service_name='s3',
    ibm_api_key_id='0SDHDYl-Jno0gJpAoaf9eAdkL51SiB-ed0vfOHfIwp41',
    ibm_auth_endpoint="https://iam.eu-de.bluemix.net/oidc/token",
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.eu-geo.objectstorage.service.networklayer.com')

body = client_c3fe26565e19406dad94b51edbfa2846.get_object(Bucket='courseracapstoneclusteringproblem-donotdelete-pr-edwrvwogd6jjyn',Key='Geospatial_Coordinates.csv')['Body']
# add missing __iter__ method, so pandas accepts body as file-like object
if not hasattr(body, "__iter__"): body.__iter__ = types.MethodType( __iter__, body )

# If you are reading an Excel file into a pandas DataFrame, replace `read_csv` by `read_excel` in the next statement.
df_data_0 = pd.read_csv(body)
df_data_0.head()

df_data_0.rename(columns={"Postal Code": "PostalCode"},inplace = True)

df_data_0.head()


# In[9]:


final_df = df.merge(df_data_0, on='PostalCode')


# In[10]:


final_df.head()


# <h1>Filter based on Borough containing Toronto</h1>

# In[11]:


toronto_data = final_df[final_df['Borough'].str.contains('Toronto')].reset_index(drop=True)
toronto_data.shape


# In[12]:


address = 'Toronto'

geolocator = Nominatim(user_agent="toronto_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude


# In[13]:


# create map of Toronto using latitude and longitude values
map_toronto = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(toronto_data['Latitude'], toronto_data['Longitude'], toronto_data['Neighborhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  


# In[14]:


map_toronto


# In[15]:


CLIENT_ID = '0Y3REBSEKOWVIBXDQ3XYD05DYJFPEGQYDDVOLUPTN0EYMWZ5' # your Foursquare ID
CLIENT_SECRET = 'T0TSRWZ3SP2ZAQVQI0GDJ52F51C3RLF1WELB1G0AOUCH0F3F' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version


# In[16]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        #print(name)
        LIMIT = 100    
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[17]:


toronto_venues = getNearbyVenues(names=toronto_data['Neighborhood'],
                                   latitudes=toronto_data['Latitude'],
                                   longitudes=toronto_data['Longitude']
                                  )


# In[18]:


toronto_venues.shape


# In[19]:


toronto_venues.head()


# In[20]:


toronto_venues.groupby('Neighborhood').count()


# In[21]:


# one hot encoding
toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
toronto_onehot['Neighborhood'] = toronto_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot = toronto_onehot[fixed_columns]

toronto_onehot.head()


# In[22]:


toronto_grouped = toronto_onehot.groupby('Neighborhood').mean().reset_index()
toronto_grouped


# In[23]:


num_top_venues = 5

for hood in toronto_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = toronto_grouped[toronto_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# In[24]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[25]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = toronto_grouped['Neighborhood']

for ind in np.arange(toronto_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# In[26]:


# set number of clusters
kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# In[27]:


# add clustering labels
neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

toronto_merged = toronto_data

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
toronto_merged = toronto_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

toronto_merged.head() # check the last columns!


# In[28]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'], toronto_merged['Neighborhood'], toronto_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:




