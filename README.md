# Warcworker
A dockerized queued high fidelity web archiver based on [Squidwarc](https://github.com/N0taN3rd/Squidwarc) (Chrome headless), RabbitMQ and a small web frontend. Using the scripting abilities of Squidwarc, you can add scripts that should be run for a specific crawl (e.g. src-set enrichment, comment expansion etc).

<img src="https://user-images.githubusercontent.com/19284/43676896-e4c3276e-97f9-11e8-815c-0ab5c1cc254f.png" alt="screenshot" width="50%" />

## Installation
Copy .env_example to .env. Update information in .env.

Start with `docker-compose up -d --scale worker=3` (wait a minute for everything to start up)

## Archiving and playback
Open web front end at http://0.0.0.0:5555 to enter URLs for archiving. You can prefill the text fields with the `url` and `description` request parameters. Play back the resulting WARC-files with [Webrecorder Player](https://github.com/webrecorder/webrecorderplayer-electron)

## Using
### Bookmarklet
Add a bookmarklet to your browser with the following link:

`javascript:window.open('http://0.0.0.0:5555/?url='+encodeURIComponent(location.href));window.focus();`

Now you have single click web archiving from your browser.


### Command line
To use from the command line with curl:

`curl -d "scripts=srcset&scripts=scroll_everything&url=https://www.peterkrantz.se/" -X POST http://0.0.0.0:5555/process/`


### Archivenow handler
To use from [archivenow](https://github.com/oduwsdl/archivenow) add a handler file `handlers/ww_handler.py` like this:

```python
import requests
import json

class WW_handler(object):

    def __init__(self):
        self.enabled = True
        self.name = 'Warcworker'
        self.api_required = False

    def push(self, uri_org, p_args=[]):
        msg = ''
        try:
	    # add scripts in the order you want them to be run on the page
            payload = {"url":uri_org, "scripts":["scroll_everything", "srcset"]}

            r = requests.post('http://0.0.0.0:5555/process/', timeout=120,
                    data=payload,
                    allow_redirects=True)

            r.raise_for_status()
            return "%s added to queue" % uri_org

        except Exception as e:
            msg = "Error (" + self.name+ "): " + str(e)
        return msg
```
