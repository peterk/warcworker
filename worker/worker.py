import time
import os
import glob
import json
import shutil
import re
import sys
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
#from mailjet_rest import Client
import logging
import traceback
import pika
import subprocess



def handle_job(message):
    """Start working on a job.
    """
    logging.info(f"Started working on {message}")

    try:
        jdata = json.loads(message)
        jobid = jdata["jobid"]
        output_path = jdata["warc"]["output"]

        # make output dir
        os.makedirs(output_path, exist_ok=True)

        # write job to file in output dir
        with open(f"{output_path}/crawl_job.json", 'w') as outfile:
            json.dump(jdata, outfile)
            logging.info(f"Wrote {output_path}/crawl_job.json")

        # run squidwarc
        subprocess.run(f"node --harmony index.js -c {output_path}/crawl_job.json", cwd="/usr/src/app/Squidwarc", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logging.info(f"Job {jobid} done!")

    except Exception:
        logging.error("Handle job broke", exc_info=True)




def callback(ch, method, properties, body):
    """Work on job from message queue."""
    logging.info(f"In callback for {body}...")
    handle_job(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    logging.info(f"Sent ack for {body}...")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting worker...")
    logging.info(f"Creds {os.environ['RABBITMQ_DEFAULT_USER']}")

    credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq', port=5672, heartbeat_interval=600, blocked_connection_timeout=300, virtual_host='/', credentials=credentials, connection_attempts=20, retry_delay=4))
    channel = connection.channel()
    channel.queue_declare(queue='archivejob', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='archivejob')
    logging.info("Started consuming queue...")
    channel.start_consuming()
