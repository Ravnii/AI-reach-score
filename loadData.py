import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

def load_data():

    train_text = []
    train_label = []

    for x in range(5):
        with open('./article_text.txt') as f:
            train_text.append(f.read())
        train_label.append(19.22)

    return (train_text, np.array(train_label))

train_data = load_data()

train_text = train_data[0]
train_label = train_data[1]
val_text = train_data[0]

NGRAM_RANGE = (1, 2)

TOP_K = 20000

TOKEN_MODE = 'word'

MIN_DOCUMENT_FREQUENCY = 2

def ngram_vectorize(train_texts, train_labels, val_texts):

    kwargs = {
            'ngram_range': NGRAM_RANGE,
            'dtype': np.float32,
            'strip_accents': 'unicode',
            'decode_error': 'replace',
            'analyzer': TOKEN_MODE,
            'min_df': MIN_DOCUMENT_FREQUENCY,
    }

    vectorizer = TfidfVectorizer(**kwargs)

    x_train = vectorizer.fit_transform(train_texts)

    x_val = vectorizer.transform(val_texts)

    # Select top 'k' of the vectorized features.
    selector = SelectKBest(f_classif, k=min(TOP_K, x_train.shape[1]))
    selector.fit(x_train, train_labels)
    x_train = selector.transform(x_train).astype('float32')
    x_val = selector.transform(x_val).astype('float32')
    return x_train, x_val

vectors = ngram_vectorize(train_texts=train_text, train_labels=train_label, val_texts=val_text)

print(vectors)
