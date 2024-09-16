import sqlite3
from datetime import datetime
from urllib.parse import urlparse
import logging

from .db_utils import _catch_errors, _logsql, summarize_text, translate_text, parse_date, clean_string

class ArticleDB:
    '''
    This class represents a database of news articles.
    It is backed by sqlite3 and designed to have no external dependencies and be easy to understand.

    The following example shows how to add urls to the database.

    >>> db = ArticleDB()
    >>> len(db)
    0
    >>> db.add_url(ArticleDB._TESTURLS[0])
    >>> len(db)
    1

    Once articles have been added,
    we can search through those articles to find articles about only certain topics.

    >>> articles = db.find_articles('Economía')

    The output is a list of articles that match the search query.
    Each article is represented by a dictionary with a number of fields about the article.

    >>> articles[0]['title']
    'La creación de empleo defrauda en Estados Unidos en agosto y aviva el temor a una recesión | Economía | EL PAÍS'
    >>> articles[0].keys()
    ['rowid', 'rank', 'title', 'publish_date', 'hostname', 'url', 'staleness', 'timebias', 'en_summary', 'text']
    '''

    _TESTURLS = [
        'https://elpais.com/economia/2024-09-06/la-creacion-de-empleo-defrauda-en-estados-unidos-en-agosto-y-aviva-el-fantasma-de-la-recesion.html',
        'https://www.cnn.com/2024/09/06/politics/american-push-israel-hamas-deal-analysis/index.html',
        ]

    def __init__(self, filename=':memory:'):
        self.db = sqlite3.connect(filename)
        self.db.row_factory=sqlite3.Row
        self.logger = logging
        self._create_schema()

    def _create_schema(self):
        '''
        Create the DB schema if it doesn't already exist.

        The test below demonstrates that creating a schema on a database that already has the schema will not generate errors.

        >>> db = ArticleDB()
        >>> db._create_schema()
        >>> db._create_schema()
        '''
        sql = '''
        CREATE VIRTUAL TABLE IF NOT EXISTS articles
        USING FTS5 (
            title,
            text,
            hostname,
            url,
            publish_date,
            crawl_date,
            lang,
            en_translation,
            en_summary
            );
        '''
        self.db.execute(sql)
        self.db.commit()


    def find_articles(self, query, limit=10, timebias_alpha=1):
        '''
        Return a list of articles in the database that match the specified query.

        Lowering the value of the timebias_alpha parameter will result in the time becoming more influential.
        The final ranking is computed by the FTS5 rank * timebias_alpha / (days since article publication + timebias_alpha).
        
        '''
        keywords = [clean_string(kw) for kw in query.split(",")]  # Split query into keywords
        query_placeholder = ' OR '.join([f'articles MATCH ?' for _ in keywords])  
        sql = f'''
            SELECT rowid, rank, title, publish_date, hostname, url, en_summary, text
            FROM articles
            WHERE {query_placeholder}
            LIMIT ?;
        '''
        _logsql(sql)

        articles = []
        cursor = self.db.cursor()
        params = keywords + [limit]  # Add the limit as the last parameter
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # rank articles
        current_date = datetime.now()  # This is a naive datetime object
        for row in rows:
            publish_date = parse_date(row['publish_date'])
            if publish_date:
                # Ensure both dates are naive by removing timezone info
                publish_date = publish_date.replace(tzinfo=None)
                days_since_publication = (current_date - publish_date).days
            else:
                days_since_publication = float('inf')  # If no publish date, use a large value

            # Handle cases where rank might be None
            rank = row['rank'] if row['rank'] is not None else 0
            timebias = (rank * timebias_alpha) / (days_since_publication + timebias_alpha)

            articles.append({
                'rowid': row['rowid'],
                'rank': rank,
                'title': row['title'],
                'publish_date': row['publish_date'],
                'hostname': row['hostname'],
                'url': row['url'],
                'en_summary': row['en_summary'],
                'text': row['text'],
                'timebias': timebias
            })

        articles.sort(key=lambda x: x['timebias'], reverse=True)
        return articles

    @_catch_errors
    def add_url(self, url, recursive_depth=0, allow_dupes=False):
        '''
        Download the url, extract various metainformation, and add the metainformation into the db.

        By default, the same url cannot be added into the database multiple times.

        >>> db = ArticleDB()
        >>> db.add_url(ArticleDB._TESTURLS[0])
        >>> db.add_url(ArticleDB._TESTURLS[0])
        >>> db.add_url(ArticleDB._TESTURLS[0])
        >>> len(db)
        1

        >>> db = ArticleDB()
        >>> db.add_url(ArticleDB._TESTURLS[0], allow_dupes=True)
        >>> db.add_url(ArticleDB._TESTURLS[0], allow_dupes=True)
        >>> db.add_url(ArticleDB._TESTURLS[0], allow_dupes=True)
        >>> len(db)
        3

        '''
        from bs4 import BeautifulSoup
        import requests
        import metahtml
        logging.info(f'add_url {url}')

        if not allow_dupes:
            logging.debug(f'checking for url in database')
            sql = '''
            SELECT count(*) FROM articles WHERE url=?;
            '''
            _logsql(sql)
            cursor = self.db.cursor()
            cursor.execute(sql, [url])
            row = cursor.fetchone()
            is_dupe = row[0] > 0
            if is_dupe:
                logging.debug(f'duplicate detected, skipping!')
                return

        logging.debug(f'downloading url')
        try:
            response = requests.get(url)
        except requests.exceptions.MissingSchema:
            # if no schema was provided in the url, add a default
            url = 'https://' + url
            response = requests.get(url)
        parsed_uri = urlparse(url)
        hostname = parsed_uri.netloc

        logging.debug(f'extracting information')
        parsed = metahtml.parse(response.text, url)
        info = metahtml.simplify_meta(parsed)

        if info['type'] != 'article' or len(info['content']['text']) < 100:
            logging.debug(f'not an article... skipping')
            en_translation = None
            en_summary = None
            info['title'] = None
            info['content'] = {'text': None}
            info['timestamp.published'] = {'lo': None}
            info['language'] = None
        else:
            logging.debug('summarizing')
            if not info['language'].startswith('en'):
                en_translation = translate_text(info['content']['text'])
            else:
                en_translation = None
            en_summary = summarize_text(info['content']['text'])

        logging.debug('inserting into database')
        sql = '''
        INSERT INTO articles(title, text, hostname, url, publish_date, crawl_date, lang, en_translation, en_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        _logsql(sql)
        cursor = self.db.cursor()
        cursor.execute(sql, [
            info['title'],
            info['content']['text'], 
            hostname,
            url,
            info['timestamp.published']['lo'],
            datetime.now().isoformat(),
            info['language'],
            en_translation,
            en_summary,
            ])
        self.db.commit()

        logging.debug('recursively adding more links')
        if recursive_depth > 0:
            for link in info['links.all']:
                url2 = link['href']
                parsed_uri2 = urlparse(url2)
                hostname2 = parsed_uri2.netloc
                if hostname in hostname2 or hostname2 in hostname:
                    self.add_url(url2, recursive_depth-1)
        
    def __len__(self):
        sql = '''
        SELECT count(*)
        FROM articles
        WHERE text IS NOT NULL;
        '''
        _logsql(sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]