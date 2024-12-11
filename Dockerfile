# Use Python 3.9 slim image
FROM python:alpine

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .
COPY bot/ bot/

# Set environment to production
ENV ENVIRONMENT=production

# Run the bot
CMD ["python", "main.py"] 