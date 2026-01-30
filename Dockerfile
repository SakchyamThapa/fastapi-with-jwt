# Step 1: Use official Python image
FROM python:3.12-slim

# Step 2: Set working directory inside container
WORKDIR /app

# Step 3: Copy requirements first (for caching)
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy project files
COPY . .

# Step 6: Expose port (FastAPI default)
EXPOSE 8000

# Step 7: Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
