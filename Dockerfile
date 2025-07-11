# 1. Base Image
FROM python:3.11-slim

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set Working Directory
WORKDIR /app

# 4. Install System Dependencies (for audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg

# 5. Install Python Dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Code
COPY . .

# 7. Create necessary directories for the application
# These can be mounted as volumes in a production environment
RUN mkdir -p /app/uploads /app/transcripts /app/config /app/logs

# 8. Expose Port
# The application runs on port 5000
EXPOSE 5000

# 9. Command to Run the Application
# Runs the web server in production mode using gunicorn
CMD ["python", "run.py", "web", "--prod", "--host", "0.0.0.0", "--port", "5000"] 