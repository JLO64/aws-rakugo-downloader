# Sets the base image for subsequent instructions
FROM ubuntu:22.04
# Sets the working directory in the container  
WORKDIR /app
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev
# Copies the files to the working directory
COPY templates/ /app/templates/
# Copies the dependency files to the working directory
COPY requirements.txt /app/requirements.txt
# Install dependencies
RUN pip install -r requirements.txt
# Copies everything to the working directory
COPY . /app
# Command to run on container start    
CMD [ "python3" , "./flask-app.py" ]
