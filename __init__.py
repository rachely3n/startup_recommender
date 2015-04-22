from flask import Flask, render_template
from flask import redirect,url_for
from flask import json
from flask import request
import json 
# sounds like i shouldn't use a trailing slash
# https://github.com/scriptish/scriptish/wiki/GM_xmlhttpRequest
#http://blog.luisrei.com/articles/flaskrest.html
#http://stackoverflow.com/questions/15080672/how-to-post-data-structure-like-json-to-flask
app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'hello there'
	return render_template('home.html')

@app.route('/process',methods= ['GET','POST'])
def poopy(): 
	return render_template('process.html')
	# return 'test'

@app.route('/foo',methods= ['GET','POST'])
def get_path():
	# return 'test'
	# error = None
	print len(request.args)
	if request.method == 'POST':
		# temp = request.get_json().path
		temp = json.loads(request.data)
		return temp["path"]
		# print json.loads(request.data)
		# return request.method
	#check if json?, need to check mimetype is application/json
	elif request.method == 'GET' and request.args.get("code") is not None:
		print "meep"
		temp = json.loads(request.data)
	else: 
		print request.args.get("code")
		return 'eep,error'
	return 'derp'

if __name__ == '__main__':
	app.run(debug = True)
