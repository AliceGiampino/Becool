from flask import Flask, render_template, request
import requests
import previsioni as pv

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
	return render_template("try.html")
 
@app.route('/result', methods = ['GET'])
def result():
	#if request.method == 'GET':
	#result1 = request.form.get('Position')
	result2 = request.args.get('Position')
	#result3 = request.values.get('Position')
	#print(, result2, result3)
	prev = pv.previsioni(pv.dataset(result2))
	return render_template("try.html", prev=prev, controllo=True)



if __name__ == "__main__":
	app.run(debug=True)

