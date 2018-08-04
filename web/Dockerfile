FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
ENV LISTEN_PORT 8080
EXPOSE 8080
RUN apk add --no-cache git
COPY ./app /app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
