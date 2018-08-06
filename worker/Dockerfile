FROM zenika/alpine-chrome

USER root
RUN apk add git
RUN apk add --update make
RUN apk add --update g++
RUN apk add --update vim
RUN apk add --update bash

RUN mkdir -p /archive
EXPOSE 9222

# install squidwarc while we have access to python 2.7
RUN git clone https://github.com/N0taN3rd/Squidwarc.git
WORKDIR Squidwarc
RUN npm install

# switch to python 3
RUN apk del python
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -r /root/.cache

WORKDIR /usr/src/app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./worker.sh worker.sh
COPY ./worker.py worker.py

RUN chmod +x worker.sh

USER chrome
ENTRYPOINT []
CMD ["/usr/src/app/worker.sh"]
