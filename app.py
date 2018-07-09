from __future__ import print_function  # In python 2.7
from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime, timedelta
import dill
import sys
import previsioni as pv
import pandas as pd
import numpy as np
import time
import geocoder
from bokeh.palettes import brewer
from bokeh.plotting import figure, output_file
from bokeh.models import Span
from bokeh.embed import components

app = Flask(__name__)
app.vars = {}


app.add_url_rule('/assets/<path:filename>', endpoint='assets', view_func=app.send_static_file)

date_time = datetime.now() 
date_time_limit = datetime.now() + timedelta(days=5)
dt_string = date_time.strftime('%Y-%m-%d %H:%M:%S')
dt_string_limit = date_time_limit.strftime('%Y-%m-%d %H:%M:%S')


@app.route('/', methods=['GET', 'POST'])
def get_prev():
	if request.method == 'POST':
		result = request.form
		location = request.values.get('Position')
		date_prev = str(request.values.get('date'))
		date_time = datetime.strptime(date_prev, '%Y-%m-%d  %H:%M:%S')
		mese = date_time.month
		giorno = int(date_time.weekday())
		
		loc = geocoder.google(location)
		k=0
		while loc.latlng == None and k<15:
			loc = geocoder.google(location)
			k+=1
		cord = loc.latlng
		
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

		output_file("tools_hover_tooltip_image.html")

		ramp = np.array([np.linspace(0, 10, 200)]*20)

		data = dict(image=[ramp],
					squared=[ramp**2],
					pattern=['smooth ramp'],
					x=[10, 10, 25],
					y=[20, 20, 5],
					dw=[20,  20, 10],
					dh=[10,  10, 25])

		p = figure( x_range=(10, 30), y_range=(20, 30), toolbar_location=None, plot_height=250, tools='hover,wheel_zoom')
		p.image(source=data, image='image', x='x', y='y', dw='dw', dh='dh', palette='Viridis256') #'Inferno256'
		p.axis.axis_label = None
		p.axis.visible = False
		p.grid.grid_line_color = None
		p.background_fill_color = None

		p.ray(x=[0],y=[0],length=300, angle=0, color='red', legend="The PM10 prevision is "+str(prevision)+' µg/m3.')

		vline = Span(location=(prevision*1.0*20)/100+10, dimension='height',line_color='red', line_width=3)
		p.renderers.extend([vline])
		script, div = components(p)
		return render_template("try.html", _anchor='prev', prevision=prevision, script=script, div=div, cord=cord, location=location, 
								giorno=giorno, mese=mese, dt_string=date_prev, dt_string_limit=dt_string_limit_post, show_prev='prev')
	else:
		
		return render_template('try.html', dt_string=dt_string, dt_string_limit=dt_string_limit, show_prev=False)

		
if __name__ == "__main__":
	app.run(debug=True)

