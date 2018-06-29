import math
import pandas as pd
import numpy as np
import geocoder
import requests
#import pickle
from sklearn.externals import joblib

def haversine(l1, l2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1 = l1[0]
    lon1 = l1[1]
    lat2 = l2[0]
    lon2 = l2[1]    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km


def dataset(position):
	#from math import radians, cos, sin, asin, sqrt
	feature_name = ['Temperature', 'Temp_t_1', 'Temp_t_2', 'Humidity', 'Wind Speed',
       'Densita', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
       'Saturday', 'Sunday', 'January', 'February', 'March', 'April',
       'May', u'June', 'July', 'August', 'September', 'October',
       'November', 'December', 'Winter', 'Spring', 'Summer', 'Autumn',
       'Arese', 'Cassano_d_Adda', 'Limito', 'Magenta', 'Milano_Pascal',
       'Milano_Verziere', 'Milano_via_Senato', 'Robecchetto',
       'Trezzo_d_Adda', 'Turbigo', 'Vigevano']
	   
	df = pd.DataFrame(0, index=np.arange(1), columns=feature_name)
	location = position
	loc = geocoder.google(location)
	k=0
	while loc.latlng == None and k<5:
		loc = geocoder.google(location)
		k+=1
	cord = loc.latlng
	sensori = pd.read_csv('sensori.csv',sep=';')
	for i in range(len(sensori.coordinate)):
		if type(sensori.coordinate[i]) == str:
			a = sensori.coordinate[i].replace('[', '').replace(']', '').split()
			a[0] = a[0].replace(',', '')
			sensori.coordinate[i] = [float(x) for x in a]
	km = 0
	for i in range(len(sensori)):
		best = ''
		if km != 0 and haversine(cord, sensori.coordinate[i]) < km:
			best = sensori.Sensore[i]
		else:
			km = haversine(cord, sensori.coordinate[i])
	df[best] = 1
	dens = pd.read_csv('dens.csv', sep=';')
	location = location.lower().split(', ')
	for j in range(len(dens.Comune)):
		if location[1].strip() == dens.Comune[j].lower():
			df['Densita'] = dens.Dens[j]
	
	r = requests.get('http://api.openweathermap.org/data/2.5/forecast?id=3173435&APPID=a33963f6e9e1d95956e7655426d493bc')
	prova = r.json()
	df['Temperature'] = prova['list'][2]['main']['temp'] - 273.15
	df['Temp_t_1'] = prova['list'][1]['main']['temp'] - 273.15
	df['Temp_t_2'] = prova['list'][0]['main']['temp'] - 273.15
	df['Humidity'] = prova['list'][2]['main']['humidity']
	df['Wind Speed'] = prova['list'][2]['wind']['speed']
	
	df['Thursday'] = 1
	df['June'] = 1
	
	return df
	


def previsioni(df):
	filename = 'model.sav'
	loaded_model = joblib.load(filename)
	return loaded_model.predict(df)




















