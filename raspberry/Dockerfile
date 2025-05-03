FROM python:3.13-slim

WORKDIR /server

COPY . .

EXPOSE ${SERVER_PORT}

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "server.py"]

