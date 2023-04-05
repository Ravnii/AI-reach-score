import json
from config import config
from urllib.request import urlopen

def call_api():
    """ Get article data from api endpoint """

    # Get url from config file
    param = config("api.ini", "articles")
    url = param['url']

    # Connect to API end point
    print("Fetching data from API endpoint...")
    response = urlopen(url)

    return json.loads(response.read())

def call_file():
    """ Get article data from file """

    # Open and read the data from file
    print("Fetching data from file...")
    with open('./articles.json') as f:
        return json.loads(f.read())
