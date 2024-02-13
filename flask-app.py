# Importing required functions 
from flask import Flask, request, render_template 
import aws_rakugo_downloader
import threading, os

# Flask constructor 
app = Flask(__name__) 

# Global variable to track if a thread is running
thread_running = False

# Root endpoint 
@app.route('/', methods=['GET']) 
def index(): 
	## Display the HTML form template 
	return render_template('index.html') 

# `read-form` endpoint 
@app.route('/read-form', methods=['POST']) 
def read_form(): 
	global thread_running

	# Get the form data as Python ImmutableDict datatype 
	data = request.form 

	# Check if a thread is already running
	if thread_running:
		return {"error": "A download is already in progress. Please wait until it finishes."}, 429

	write_rajiko_list_to_file(data['rajiko-list'])

	# Start a new thread that will run the function in the background
	# thread = threading.Thread(target=aws_rakugo_downloader.main, args=(data['rajiko-list'],))
	thread = threading.Thread(target=start_list)
	thread.start()

	# Set the global variable to True
	thread_running = True

	## Return the extracted information 
	return {"success": "Download has begun of the list!"}, 200

def start_list():
	global thread_running
	try:
		aws_rakugo_downloader.main('./list.txt', './logfile.txt')
		thread_running = False
	except Exception as e:
		print(e)
		thread_running = False
		raise e

def write_rajiko_list_to_file(rajiko_list):
	filepath = "./list.txt"
	if os.path.exists(filepath):
		os.remove(filepath)
	with open(os.path.expanduser(filepath), 'a') as f:
		f.write(rajiko_list)

# Main Driver Function 
if __name__ == '__main__': 
	# Run the application on the local development server 
	app.run(host='0.0.0.0')
