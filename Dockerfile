# Use the lightweight Alpine-based Python 3.10 image as a base image
FROM python:3.10-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Some Python packages might require system dependencies. 
# Uncomment the following line if you need any system dependencies installed:
# RUN apk add --no-cache <dependency-name>

# Copy the requirements file into the container at the current working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY app.py .
# COPY src/ src/

# Expose the Flask default port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
