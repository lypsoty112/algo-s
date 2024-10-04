# Use an official Python runtime as the base image
FROM python:3.9-slim

# Install cron and tzdata
RUN apt-get update && apt-get -y install cron tzdata

# Set the time zone to Brussels
RUN ln -fs /usr/share/zoneinfo/Europe/Brussels /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the environment variable for Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Create a script to export environment variables and run the Python script
RUN echo '#!/bin/bash\n\
source /app/env_vars.sh\n\
/usr/local/bin/python /app/main.py' > /app/run_script.sh && \
    chmod +x /app/run_script.sh

# Create a cron job file
RUN echo "30 15 * * 1-5 /app/run_script.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/app-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/app-cron

# Apply cron job
RUN crontab /etc/cron.d/app-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD printenv | grep -v "no_proxy" > /app/env_vars.sh && \
    sed -i 's/^/export /' /app/env_vars.sh && \
    cron && tail -f /var/log/cron.log