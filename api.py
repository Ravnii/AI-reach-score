import json
import datetime
from config import config
from urllib.request import urlopen

def fetch(next_page = ""):
    """ Get article data from api endpoint """

    # Get url from config file
    params = config("api.ini", "articles")

    if not next_page:
        url = params['url'] + '?modified_since=' + get_timestamp(True) + '&modified_until=' + get_timestamp(False)
    else:
        url = params['domain'] + next_page

    # Connect to API end point
    print("Fetching data from API endpoint...")
    response = urlopen(url)

    return json.loads(response.read())

def get_timestamp(since):
    now = datetime.datetime.now()

    delta = now - datetime.timedelta(days=1, hours=now.hour, minutes=now.minute, seconds=now.second)

    ts = datetime.datetime.timestamp(delta)

    if since:
        return str(int(ts))
    else:
        return str(int(ts) + 86400)
