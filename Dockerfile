# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update --fix-missing && \
    apt-get install -y --fix-missing git build-essential docker.io software-properties-common zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8969 available to the world outside this container
EXPOSE 8969

# Run streamlit when the container launches
CMD ["streamlit", "run", "RoboTF_LLM_Tools.py", "--server.port", "8969"]