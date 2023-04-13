import pandas as pd
import api
from tqdm import tqdm
from random import randint
from danlp.models import load_bert_base_model
from htmlstripper import strip_tags
import database

model = load_bert_base_model()

def create_rows():
    """ Create the data for the csv file """

    json_data = api.fetch()

    next_page = json_data['metadata']['next']

    articles = json_data['data']

    rows = []

    while True:

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
                reach_scores = database.get_reach_score(article['article_uuid'])
                for tuple in reach_scores:
                    score = tuple[0]
                    hostname = tuple[1]
                    rows.append([article['article_uuid'], score, hostname, sentence_embedding.numpy()])

        if not next_page:
            break

        json_data = api.fetch(next_page)

        next_page = json_data['metadata']['next']

        articles = json_data['data']

    return rows

def create_csv():
    """ Create csv file by merging with the old one and remove duplicates """

    columns = ['article_uuid', 'score', 'hostname', 'embedding']

    data = create_rows()

    df = pd.DataFrame(data=data, columns=columns)

    df.set_index('article_uuid', drop=True, inplace=True)

    print("Saving new data to csv")
    df.to_csv('articles.csv', header=False, mode='a', index_label='article_uuid')

    new_df = pd.read_csv('articles.csv', index_col='article_uuid')

    print(new_df)

if __name__ == '__main__':
    create_csv()
    database.disconnect()
