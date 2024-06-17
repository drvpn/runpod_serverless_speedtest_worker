# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app/ /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade -r /app/requirements.txt --no-cache-dir

# Run app/handler.py when the container launches
CMD ["python", "-u", "/app/handler.py"]
