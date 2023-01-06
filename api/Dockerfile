FROM python:3.11-slim

# Install dependencies

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential 

# Install Python dependencies

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip 
RUN pip install -r /app/requirements.txt

COPY src/ app/

# Run the application

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
