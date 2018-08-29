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


def make_job(jobid, output_path, seeds=[], description="", scripts=[]):
    """Create json for crawl job.
    """

    data = {}
    data["jobid"] = jobid
    data["description"] = description

    # create concatenated script file for this job.
    if scripts:
        jobscript_file = f"/scripts/job/{jobid}.js"
        with open(jobscript_file, 'w') as outfile:

            # add utils
            outfile.write("const utils = require(\"/scripts/utils/utils\");\n")

            # write methods. Each script file should contain a function with the same name as the script file.
            for script in scripts:
                with open(f"/scripts/{script}") as infile:
                    outfile.write(infile.read())

            ## write method calls
            outfile.write("\n\nmodule.exports = async function (page) {\n")
            for script in scripts:
                function_call = "\tawait " + script.replace(".js","") + "(page);"
                outfile.write(function_call + "\n")
                outfile.write("\tawait utils.delay(2000);\n")
            outfile.write("}\n")
            
        data["script"] = jobscript_file

    data["use"] = "puppeteer"
    data["headless"] = True
    data["mode"] = "page-only"
    data["depth"] = 1
    data["seeds"] = seeds
    data["warc"] = {}
    data["warc"]["naming"] = "url"
    data["warc"]["output"] = output_path
    data["warc"]["append"] = True
    data["executablePath"] = "/usr/bin/google-chrome-stable"
    data["connect"] = {}
    data["connect"]["launch"] = True
    data["connect"]["host"] = "localhost"
    data["connect"]["port"] = 9222
    data["crawlControl"] = {}
    data["crawlControl"]["globalWait"] = 60000
    data["crawlControl"]["inflightIdle"] = 2000
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

    # load available scripts
    scripts = []
    for file in os.listdir("/scripts"):
        if file.endswith(".js"):
            scripts.append(str(file).replace(".js",""))

    return render_template('index.html', url=url, description=description, scripts=scripts)


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

    # list the scripts that should be run by the crawler. Scripts need to exist
    # in the /scripts dir and will be bundled to a new file.
    form_scripts = request.form.getlist("scripts")
    scripts = []
    if form_scripts:
        scripts = [script + ".js" for script in form_scripts if os.path.exists("/scripts/" + script + ".js")]

    # Make output directory path based on <base path>/<harvest year>/<harvest month>/<harvest day>/<job id>...
    # Users can map /archive in docker to access warcs.
    output_path = f"/archive/{now.year}/{str(now.month).zfill(2)}/{str(now.day).zfill(2)}/{jobid}"

    # Add crawl request to queue
    message = make_job(jobid, output_path, seeds, description, scripts)
    connection = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', credentials, heartbeat_interval=600, blocked_connection_timeout=300))
    channel = connection.channel()
    channel.queue_declare(queue='archivejob', durable=True)
    channel.basic_publish(exchange='', routing_key='archivejob', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
    connection.close()

    app.logger.info(f"Created job {message}")

    return render_template('thankyou.html')
            


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=DEBUG, port=8000)
