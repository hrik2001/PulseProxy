from flask import Flask , render_template , request , Response , url_for , make_response
from requests import get
from werkzeug.datastructures import Headers
import re

#TODO:
#1) Make a basic proxy that at least shows basic html files (but not images)
#	1.1) format for now : <pulseproxy ip>/<website_dns>/<directory>
#	1.2) later on when we will access the site we will ask user what site they wanna surf, that site will be stored in a session cookie
#		 then it will behave exactly like the site we are proxying, just accessible from different dns
#2) Make the proxy load multimedia files (by changin a href statements so that user sends request to our server)
#	2.1) by reading the MIMETYPE from content-type header of the response and using the function flask.send_file
#	2.2) a function which will every link be it local or global into proxy equivalent link so traffic always passes through proxy
#	2.3) use a virtual file system to relay files, file should be of certain size
#3) Handle https requests
#4) Make proxy load and update cookies in the User's computer

app = Flask(__name__)

#TODO:
#come up with an universal proxy
HTML_REGEX = re.compile(r'((?:src|action|href)=["\'])/')
JQUERY_REGEX = re.compile(r'(\$\.(?:get|post)\(["\'])/')
JS_LOCATION_REGEX = re.compile(r'((?:window|document)\.location.*=.*["\'])/')
CSS_REGEX = re.compile(r'(url\(["\']?)/')

REGEXES = [HTML_REGEX, JQUERY_REGEX, JS_LOCATION_REGEX, CSS_REGEX]

@app.route("/")
def home():
	return "PulseProxy"

@app.route("/<site>", methods = ["GET" , "POST", "PUT", "DELETE"])
@app.route("/<site>/", methods = ["GET" , "POST", "PUT", "DELETE"])
@app.route("/<site>/<path:directory>", methods = ["GET" , "POST", "PUT", "DELETE"])
def proxy(site , directory = "" , methods = ["GET" , "POST", "PUT", "DELETE"]):
	'''
	TODO:
	Request library shouldnt be used later, rather a mechanism to forward GET and POST requests
	-for now only static GET requests work 
	'''
	print("USER ASKED FOR " + f'https://{site}/{directory}')
	#printing stuff for debugging, messy but works for fast dev

	####manipulating request part#####

	#request.headers is of type 'werkzeug.datastructures.EnvironHeaders' so we need to convert to a dictionary
	request_headers = {}
	for i in request.headers:
		request_headers[i[0]] = i[1]

	if request.method in ["POST" , "PUT"]:
		form = request.form
	else:
		form = None

	#conn = get(f'https://{site}/{directory}', headers = request_headers)
	conn = get(f'https://{site}/{directory}')
	content = b"<h1>PulseProxy</h1>"+conn.content


	root = url_for(".proxy", site=site)
	root = root[0:len(root)-1]


	for regex in REGEXES:
		try:
			content = regex.sub(r'\1%s' % root, content.decode().strip()).encode().strip()
		except:
			content = regex.sub(r'\1%s' % root, str(content)).encode().strip()

	response_headers = Headers()
	for key , value in conn.headers.items():
		response_headers.add(key , value)
	#answer = Response(response=content , status=conn.status_code , headers=response_headers , content_type=response_headers["content-type"])
	print(response_headers["content-type"] + f"  for https://{site}/{directory}")
	answer = make_response(content)

	#TODO:
	#come up with how to reply with headers
	#below code not working
	'''
	print(conn.headers)
	for key, value in conn.headers.items():
		answer.headers[key] = value
	'''
	return answer
	#return(content , conn.status_code , conn.headers)
	


if __name__ == "__main__":
	app.debug = True
	app.run()