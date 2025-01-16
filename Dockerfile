# # Copy the rest of the application code into the container at /mybot
# COPY . /new/

# # Copy the .env file into the container at /mybot/.env
# COPY .env /new/.env

# Use Python base image
FROM python:3.9-slim

# Install git (needed to fetch dependencies from GitHub)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /hello-fly

# Copy requirements.txt (make sure it is in your local directory)
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN ls -la /new  # or /app, depending on your WORKDIR

# Copy the rest of the application code
COPY . .

# Expose the port if your app listens on one (optional, depending on your app)
EXPOSE 8080

# Command to run your app (replace with your bot script or app entry point)
CMD ["python", "main.py"]

