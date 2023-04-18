FROM python:3.9.16
WORKDIR /app
ARG name=defaultValue
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
#RUN apt update && apt install nano
COPY . .
#ENTRYPOINT ["bash","sleep","10s","&&","echo","Starting Locust"]
ENTRYPOINT ["locust", "--host", "http://frontend-service:8081", "-u", "1", "--run-time", "240s"]