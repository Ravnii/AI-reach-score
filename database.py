import psycopg2
from config import config
from random import randint

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        return conn

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def get_reach_score(article_uuid):
    """ Get reach score for article """

    try:
        # Fetch from database
        cur.execute("SELECT reach_score, hostname FROM rolling_30_days_news WHERE article_id = '" + article_uuid + "'")
        row = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    if row is not None:
        return row
    else:
        return []

conn = connect()
cur = conn.cursor()

def disconnect():
    cur.close()
    conn.close()
