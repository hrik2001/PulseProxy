from flask import Flask , request , Response , url_for , make_response
from requests import get
import re
import mimetypes


#TODO:
#1) Make a basic proxy that at least shows basic html files (but not images)
#	1.1) format for now : <pulseproxy ip>/<website_dns>/<directory>
#	1.2) later on when we will access the site we will ask user what site they wanna surf, that site will be stored in a session cookie
#		 then it will behave exactly like the site we are proxying, just accessible from different dns
#2) Make the proxy load multimedia files (by changin a href statements so that user sends request to our server)
#	2.1) by reading the MIMETYPE from content-type header of the response and using the function flask.send_file
#	2.2) a function which will every link be it local or global into proxy equivalent link so traffic always passes through proxy
#	2.3) use a virtual file system to relay files, file should be of certain size
#		2.3.1)Support for integration temporary file system and flask gone :(
#3) Handle big files by streaming data from requests then streaming back to user
#4) Make proxy load and update cookies in the User's computer

app = Flask(__name__)

#TODO:
#come up with an universal proxy
HTML_REGEX = re.compile(r'((?:src|action|href)=["\'])/')
JQUERY_REGEX = re.compile(r'(\$\.(?:get|post)\(["\'])/')
JS_LOCATION_REGEX = re.compile(r'((?:window|document)\.location.*=.*["\'])/')
CSS_REGEX = re.compile(r'(url\(["\']?)/')

REGEXES = [HTML_REGEX, JQUERY_REGEX, JS_LOCATION_REGEX, CSS_REGEX]

def filename(url):
	url = url.split("/")
	if url[len(url)-1] == "":
		url = url[len(url)-2]
	else:
		url = url[len(url)-1]
	return url


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
	#The class behaves kind of like a dictionary so we are in luck.	
	request_headers = {}
	for i in request.headers:
		#BUG:
		#Sending all requests raises some exceptions in connection
		#bibi21000 at https://bibi21000.github.io/janitoo_manager_proxy/_modules/janitoo_manager_proxy/views.html
		#Whitlisted these headers, therefore I am too, Will look into why thats happening later
		if i[0] in ["Cookie", "Referer", "X-Csrf-Token"]:
			request_headers[i[0]] = i[1]
	print("REQUEST HEADERS::")
	print(request.headers)

	if request.method in ["POST" , "PUT"]:
		form = request.form
	else:
		form = None

	conn = get(f'https://{site}/{directory}', headers = request_headers , data = form)
	#conn = get(f'https://{site}/{directory}')
	

	#to prevent redirection
	if "location" in conn.headers:
		url = conn.headers["location"]
		if url.startswith("https://"):
			url = url[8:]
		elif url.startswith("https://"):
			url = url[7:]

		if url[0]=="/":
			url = site + url
		else:
			url = "/"+url
		conn.headers["location"] = url
	
	
	
	#if the link is a webpage
	if "text" in conn.headers['content-type']:		
		content = conn.content
		root = url_for(".proxy", site=site )	
		for regex in REGEXES:
			try:
				content = regex.sub(r'\1%s' % root, content.decode().strip()).encode().strip()
			except:
				content = regex.sub(r'\1%s' % root, str(content)).encode().strip()

		answer = make_response(content)
		for key, value in conn.headers.items():
			#Once again, only few whitelisted headers work or else other headers bug it up, these ones were found by hit and trial
			if key in ["Date" , "set-cookie","content-length", "connection", "content-type" , "location"]:
				answer.headers[key] = value

		return answer
	else:
		#if the link serves multimedia file
		#TODO:
		#come up with an ideal chunk size
		return Response(conn.iter_content(chunk_size = 200*1024) , content_type = conn.headers['content-type'])




if __name__ == "__main__":
	app.debug = True
	app.run()
