FROM python:3.10-slim

# Create a working directory
WORKDIR /app

# Copy requirements first, for caching
COPY requirements.txt /app/

# Install Python dependencies (including Alembic)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code, including alembic.ini and migrations/
COPY . /app

# By default, run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]