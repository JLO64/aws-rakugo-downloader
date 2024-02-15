# Importing required functions 
from flask import Flask, request, render_template 
import aws_rakugo_downloader
import threading, os, datetime

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

	write_yt_dlp_list_to_file(data['yt-dlp-list'])

	# Start a new thread that will run the function in the background
	# thread = threading.Thread(target=aws_rakugo_downloader.main, args=(data['yt-dlp-list'],))
	thread = threading.Thread(target=start_list)
	thread.start()

	# Set the global variable to True
	thread_running = True

	## Return the extracted information 
	return {"success": "Download has begun of the list!"}, 200

# 'log-data' endpoint
@app.route('/log-data', methods=['GET'])
def log_data():
    if not os.path.exists("./logs") or len(os.listdir("./logs")) == 0:
        return "<p>No logs found.</p>"
    string_to_return = ""
    dir_list = os.listdir("./logs")
    dir_list.sort()
    with open("./logs/" + dir_list[-1], 'r') as f:
        for line in f:
            string_to_return += "<p>" + line + "</p>"
    return string_to_return

def start_list():
	global thread_running
	try:
		aws_rakugo_downloader.main('./list.txt', logfile_initializer(), "America/Los_Angeles")
		thread_running = False
	except Exception as e:
		print(e)
		thread_running = False
		raise e

def logfile_initializer():
	#make a directory called logs
	if not os.path.exists("./logs"):
		os.makedirs("./logs")
	#make a file with filename in the format YYYY-MM-DD-HH-MM
	filename = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")) + ".log"
	open("./logs/" + filename, 'w')
	return "./logs/" + filename

def write_yt_dlp_list_to_file(yt_dlp_list):
	filepath = "./list.txt"
	if os.path.exists(filepath):
		os.remove(filepath)
	with open(os.path.expanduser(filepath), 'a') as f:
		f.write(yt_dlp_list)

# Main Driver Function 
if __name__ == '__main__': 
	from waitress import serve
	serve(app, host="0.0.0.0", port=5000)
