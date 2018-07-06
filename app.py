from __future__ import print_function  # In python 2.7
from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime, timedelta
import dill
import sys
import previsioni as pv
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import time

app = Flask(__name__)
app.vars = {}


app.add_url_rule('/assets/<path:filename>', endpoint='assets', view_func=app.send_static_file)

@app.route('/', methods=['GET', 'POST'])
def get_prev():
	if request.method == 'POST':
		result = request.form
		location = request.values.get('Position')
		date_prev = str(request.values.get('date'))
		if 'AM' in date_prev:
			if '12' in date_prev:
				date_prev = date_prev.replace('12', '00')
			date_prev = pd.to_datetime(date_prev).strftime('%Y-%m-%d %H:%M:%S')
		if 'PM' in date_prev:
			date_prev = pd.to_datetime(date_prev).strftime('%Y-%m-%d %H:%M:%S')
		date_time = datetime.strptime(date_prev, '%Y-%m-%d  %H:%M:%S')
		mese = date_time.month
		giorno = int(date_time.weekday())
		
		df = pv.dataset(location, date_time, giorno, mese)

		if df.shape[1] == 38:
			prev = np.zeros(1)
			prev = pv.previsioni_now(df)
		if df.shape[1] == 39:
			prev = np.zeros(1)
			prev = pv.previsioni_tom(df)
		if df.shape[1] == 40:
			prev = np.zeros(1)
			prev = pv.previsioni_all(df)
		prevision = round(float(prev[0]), 2)

		date_time_limit_post = datetime.now() + timedelta(days=5)
		dt_string_limit_post = date_time_limit_post.strftime('%m/%d/%Y %#I:%M %p')
		

		lbls = ['Low', 'Limit', 'High']
		xvalues = [-0.5, 0.5, 1.5]

		plt.yticks([])
		plt.xticks(xvalues, lbls)

		plt.rcParams["axes.grid"] = False
		plt.imshow([[0.,1.], [0.,1.]], aspect=0.2,
			  cmap = plt.cm.RdYlGn_r, 
			  interpolation = 'bicubic',
			  norm = colors.Normalize(vmin=0.0, vmax=1.0)
			)
		
		
		p= 0.0
		k = 0
		p=prevision*1.0/100
		plt.axvline(x=p)
		k = time.time()
		nome_file = './static/prev%d.png'%k
		print(nome_file)
		plt.savefig(nome_file)
		plt.clf()
		return render_template("try.html", prevision=prevision, location=location, giorno=giorno, mese=mese, dt_string=date_prev, dt_string_limit=dt_string_limit_post, nome_file=nome_file, show_prev=True)
	
	else:
		date_time_init = datetime.now()
		date_time_limit = datetime.now() + timedelta(days=5)
		dt_string = date_time_init.strftime('%m/%d/%Y %#I:%M %p')
		dt_string_limit = date_time_limit.strftime('%m/%d/%Y %#I:%M  %p')
		return render_template('try.html', dt_string=dt_string, dt_string_limit=dt_string_limit, show_prev=False)


if __name__ == "__main__":
	app.run(debug=True)

