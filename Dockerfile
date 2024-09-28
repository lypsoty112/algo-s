# Use an official Python runtime as the base image
FROM python:3.9-slim

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

# Set the environment variables
ENV NEWS_API_API_KEY=""
ENV OPENAI_API_KEY=""
ENV ALPACA_API_KEY=""
ENV ALPACA_SECRET_KEY=""
ENV POLYGON_API_KEY=""
ENV MAX_STOCKS=20
ENV MODEL_NAME=""
ENV MONGODB_URI=""
ENV MONGODB_DB_NAME=""
ENV MONGODB_COLLECTION_NAME=""

# Run the main application
CMD ["python", "main.py"]
