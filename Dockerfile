# Sets the base image for subsequent instructions
FROM ubuntu:22.04
# Sets the working directory in the container  
WORKDIR /app
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev

COPY templates/ /app/templates/
COPY requirements.txt /app/requirements.txt
COPY *.py /app/

# Install dependencies
RUN pip install -r requirements.txt

# COPY . /app
RUN mkdir ./yt-dlp-downloads
# Command to run on container start    
CMD [ "python3" , "./flask-app.py" ]
