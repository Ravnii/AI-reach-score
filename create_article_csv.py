import json
import psycopg2
import pandas as pd
from tqdm import tqdm
from random import randint
from urllib.request import urlopen
from danlp.models import load_bert_base_model
from htmlstripper import strip_tags
from database import connect
from config import config

model = load_bert_base_model()
conn = connect()
cur = conn.cursor()

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

def get_reach_score(article_uuid):
    """ Get reach score for article """

    try:
        # Fetch from database
        cur.execute("SELECT reach_score FROM rolling_30_days_news WHERE article_uuid = '" + article_uuid + "'")
        row = cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    if row is not None:
        return row[0]
    else:
        # Return random score if not found
        return randint(0, 20000)

def create_rows():
    """ Create the data for the csv file """

    # Call data provider (file or endpoint) switch as needed
    json_data = call_file()

    articles = json_data['data']

    rows = []

    print("Creating article data...")
    # Loop through all articles in data set
    for article in tqdm(articles):
        text = ''
        failure = False

        # Loop through the article content and create a text string
        for content in article['content']:
            if "text" in content['data']:
                text += ' ' + strip_tags(content['data']['text'])

        # List articles fails embedding
        try:
            article_text = article['headline'] + ' ' + article['lead'] + ' ' + text
            token_embeddings, sentence_embedding, tokenized_text = model.embed_text(article_text)
        except:
            failure = True

        if failure is False:
            score = get_reach_score(article['article_uuid'])
            rows.append([article['article_uuid'], score, sentence_embedding.numpy()])

    return rows

def create_csv():
    """ Create csv file by merging with the old one and remove duplicates """

    columns = ['article_uuid', 'score', 'embedding']

    rows = create_rows()

    df = pd.DataFrame(data=rows, columns=columns)

    df.set_index('article_uuid', drop=True, inplace=True)

    old_df = pd.read_csv('articles.csv', index_col='article_uuid')

    new_df = pd.concat([df, old_df])

    new_df = new_df[~new_df.index.duplicated(keep='last')]

    print("Saving new data to csv")
    new_df.to_csv('articles.csv')

    print(pd.read_csv('articles.csv'))

if __name__ == '__main__':
    create_csv()
    cur.close()
    conn.close()
