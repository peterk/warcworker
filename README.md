# Warcworker
A dockerized queued high fidelity web archiver based on [Squidwarc](https://github.com/N0taN3rd/Squidwarc) (Chrome headless), RabbitMQ and a small web frontend.

<img src="https://user-images.githubusercontent.com/19284/43676896-e4c3276e-97f9-11e8-815c-0ab5c1cc254f.png" alt="screenshot" width="50%" />

## Installation
Copy .env_example to .env. Update information in .env.

Start with `docker-compose up -d --scale worker=3` (wait a minute for everything to start up)

## Archiving and playback
Open web front end at http://127.0.0.1:5555 to enter URLs for archiving. You can prefill the text fields with the `url` and `description` request parameters.

Add a bookmarklet to your browser with the following link:

`javascript:window.open('http://127.0.0.1:5555/?url='+encodeURIComponent(location.href));window.focus();`

Now you have single click web archiving from your browser.

Play back the resulting WARC-files with [Webrecorder Player](https://github.com/webrecorder/webrecorderplayer-electron)
