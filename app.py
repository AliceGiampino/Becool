from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
	return render_template("try.html")
 
@app.route('/result', methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form['Position']
      return render_template("result.html",result = result)



if __name__ == "__main__":
	app.run(debug=True)

