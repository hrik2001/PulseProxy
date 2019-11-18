from flask import Flask , render_template , request
from requests import get

#TODO:
#1) Make a basic proxy that at least shows basic html files (but not images)
#	1.1) format for now : <pulseproxy ip>/<website_dns>/<directory>
#	1.2) later on when we will access the site we will ask user what site they wanna surf, that site will be stored in a session cookie
#		 then it will behave exactly like the site we are proxying, just accessible from different dns
#2) Make the proxy load multimedia files (by changin a href statements so that user sends request to our server)
#3) Handle https requests
#4) Make proxy load and update cookies in the User's computer

app = Flask(__name__)

@app.route("/")
def home():
	return "PulseProxy"

@app.route("/<site>")
@app.route("/<site>/")
@app.route("/<site>/<directory>")
def proxy(site , directory = ""):
	'''
	TODO:
	Request library shouldnt be used later, rather a mechanism to forward GET and POST requests
	-for now only static GET requests work 
	'''
	return(b"<h1>PulseProxy</h1>"+get(f'https://{site}/{directory}').content)
	


if __name__ == "__main__":
	app.debug = True
	app.run()