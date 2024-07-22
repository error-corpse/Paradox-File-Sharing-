FROM python:3.8-slim-buster
WORKDIR /app

# Install NTP
RUN apt-get update && apt-get install -y ntp

# Start NTP service
RUN service ntp start

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD python3 main.py
