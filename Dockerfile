FROM python:3.12.0b2-bullseye

COPY requirements.txt /app/
WORKDIR /app/
RUN pip install -r requirements.txt

COPY . .
CMD [ "python3", "main.py" ]