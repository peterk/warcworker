# warcworker
A dockerized queued high fidelity web archiver based on Squidwarc, RabbitMQ and a small web frontend.

# Installation
Copy .env_example to .env. Start with docker-compose up -d --scale worker=3

Open web front end at http://127.0.0.1:8000
