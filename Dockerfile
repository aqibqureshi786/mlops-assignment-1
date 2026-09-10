FROM python:3.11-slim

WORKDIR /app

# Leverage Docker layer caching for dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port 5000 as required in assignment specification
EXPOSE 5000

# Run FastAPI app using uvicorn on port 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
