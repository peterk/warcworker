from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import hashlib
from hashlib import md5
import json
import os
import urllib
import glob
import logging 
import pika
import datetime

app = Flask(__name__)
app.secret_key = os.environ["FLASK_KEY"]
DEBUG = os.environ["FLASK_DEBUG"] 
credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])


def make_job(jobid, output_path, seeds=[], description=""):
    """Create json for crawl job.
    """
    data = {}
    data["jobid"] = jobid
    data["description"] = description
    data["headless"] = True
    data["mode"] = "page-only"
    data["depth"] = 1
    data["seeds"] = seeds
    data["warc"] = {}
    data["warc"]["naming"] = "url"
    data["warc"]["output"] = output_path
    data["connect"] = {}
    data["connect"]["launch"] = False
    data["connect"]["host"] = "localhost"
    data["connect"]["port"] = 9222
    data["crawlControl"] = {}
    data["crawlControl"]["globalWait"] = 60000
    data["crawlControl"]["inflightIdle"] = 1000
    data["crawlControl"]["numInflight"] = 2
    data["crawlControl"]["navWait"] = 8000

    return json.dumps(data)


@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.route("/", methods=['GET'])
def hello():
    url = request.args.get("url", "")
    description = request.args.get("description", "")
    return render_template('index.html', url=url, description=description)


@app.route("/process/", methods=['POST'])
def process():

    url = request.form.get("url", None)
    seeds = []
    for seed in url.split("\n"):
        seeds.append(seed.strip())

    description = request.form.get("description", None)

    # Make jobid from url set and timestamp
    now = datetime.datetime.now()
    m = hashlib.md5()
    m.update(url.encode("utf-8") + now.isoformat().encode("utf-8"))
    jobid = m.hexdigest()

    # Make output directory path based on <base path>/<harvest year>/<harvest month>/<harvest day>/<job id>...
    # Users can map /archive in docker to access warcs.
    output_path = f"/archive/{now.year}/{str(now.month).zfill(2)}/{str(now.day).zfill(2)}/{jobid}"

    # Add crawl request to queue
    message = make_job(jobid, output_path, seeds, description)
    connection = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', credentials, heartbeat_interval=600, blocked_connection_timeout=300))
    channel = connection.channel()
    channel.queue_declare(queue='archivejob', durable=True)
    channel.basic_publish(exchange='', routing_key='archivejob', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
    connection.close()

    app.logger.info(f"Created job {message}")

    return render_template('thankyou.html')
            


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=DEBUG, port=8000)
