# Warcworker
A dockerized queued high fidelity web archiver based on [Squidwarc](https://github.com/N0taN3rd/Squidwarc) (Chrome headless), RabbitMQ and a small web frontend.

## Installation
Copy .env_example to .env. 

Start with `docker-compose up -d --scale worker=3` (wait a minute for everything to start up)

## Archiving and playback
Open web front end at http://127.0.0.1:8080 to enter URLs for archiving.

Add a bookmarklet to your browser with the following link:

`javascript:window.open('http://127.0.0.1:8080/?url='+encodeURIComponent(location.href));window.focus();`

Now you have single click web archiving from your browser.

Play back the resulting WARC-files with [Webrecorder Player](https://github.com/webrecorder/webrecorderplayer-electron)
