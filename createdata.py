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

    # Call data provider (file or endpoint) switch as needed
    json_data = api.call_file()

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
            score = database.get_reach_score(article['article_uuid'])
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
    database.disconnect()
