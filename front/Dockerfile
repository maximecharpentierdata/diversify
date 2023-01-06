FROM python:3.11-slim

EXPOSE 80

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ app/

ENTRYPOINT ["streamlit", "run", "/app/Home.py", "--server.port=80", "--server.address=0.0.0.0"]