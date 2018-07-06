import math
import pandas as pd
import numpy as np
import geocoder
import requests
from sklearn.externals import joblib
import calendar

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


def dataset(position, date_time, giorno, mese):
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
	while loc.latlng == None and k<15:
		loc = geocoder.google(location)
		k+=1
	cord = loc.latlng
	sensori = pd.read_csv('sensori.csv',sep=';')
	for i in range(len(sensori.coordinate)):
		if type(sensori.coordinate[i]) == str:
			a = sensori.coordinate[i].replace('[', '').replace(']', '').split()
			a[0] = a[0].replace(',', '')
			sensori.coordinate[i] = [float(x) for x in a]

	if cord != None:
		km = 0
		for i in range(len(sensori)):
			best = ''
			if km != 0 and haversine(cord, sensori.coordinate[i]) < km:
				best = sensori.Sensore[i]
			else:
				km = haversine(cord, sensori.coordinate[i])
		df[best] = 1
	else:
		print('error')

	dens = pd.read_csv('dens.csv', sep=';')
	location = location.lower().split(', ')
	for j in range(len(dens.Comune)):
		if location[1].strip() == dens.Comune[j].lower():
			df['Densita'] = dens.Dens[j]
	
	df[calendar.day_name[giorno]] = 1
	df[calendar.month_name[mese]] = 1

	w = [12, 1, 2]
	sp = [3, 4, 5]
	su = [6, 7, 8]
	if calendar.month_name[mese] in w:
		df['Winter'] = 1
	elif calendar.month_name[mese] in sp:
		df['Spring'] = 1
	elif calendar.month_name[mese] in su:
		df['Summer'] = 1
	else:
		df['Autumn'] = 1
	
	r = requests.get('http://api.openweathermap.org/data/2.5/forecast?id=3173435&APPID=a33963f6e9e1d95956e7655426d493bc')
	prova = r.json()
	a = prova['list']
	
	temp_1, temp_2, temperature, um, wind = np.NaN, np.NaN, np.NaN, np.NaN, np.NaN
	h = str(date_time)[:-5]+'00:00'

	min = 23
	for i in range(0, 22, 3):
		if min > abs(int(h[11:13])-i):
			min = abs(int(h[11:13])-i)
			change = i
        
	k = h.replace(h[10:13], ' '+str(change))
	
	for i in range(len(a)):
		for key in a[i].keys():
			if k == a[i][key]:
				temperature = a[i]['main']['temp'] - 273.15
				um = a[i]['main']['humidity']
				wind = a[i]['wind']['speed']
				df['Temperature'] = temperature
				df['Humidity'] = um
				df['Wind Speed'] = wind
				if i-8 >=0:
					temp_1 = a[i-8]['main']['temp'] - 273.15
					df['Temp_t_1'] = temp_1
				else:
					df.drop(columns=['Temp_t_1', 'Temp_t_2'], inplace=True)
					return df
				if i-16 >=0:
					temp_2 = a[i-16]['main']['temp'] - 273.15
					df['Temp_t_2'] = temp_2
				else:
					df.drop(columns='Temp_t_2')
					return df

	return df
	


def previsioni_all(df):
	filename = 'model.sav'
	loaded_model = joblib.load(filename)
	return loaded_model.predict(df)

def previsioni_tom(df):
	filename = 'model_tom.sav'
	loaded_model = joblib.load(filename)
	return loaded_model.predict(df)

def previsioni_now(df):
	filename = 'model_now.sav'
	loaded_model = joblib.load(filename)
	return loaded_model.predict(df)

