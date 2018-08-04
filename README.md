# warcworker
A dockerized queued high fidelity web archiver based on [Squidwarc](https://github.com/N0taN3rd/Squidwarc) (Chrome headless), RabbitMQ and a small web frontend.

# Installation
Copy .env_example to .env. 

Start with `docker-compose up -d --scale worker=3`

Open web front end at http://127.0.0.1:8000

Play back the resulting WARC-files with [Webrecorder Player](https://github.com/webrecorder/webrecorderplayer-electron)
