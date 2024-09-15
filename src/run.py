import argparse
import logging 

from articledb import ArticleDB
from rag import rag

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--loglevel', default='warning')
parser.add_argument('--db', default='./sql_data/ragnews.db')
parser.add_argument('--recursive_depth', default=0, type=int)
parser.add_argument('--add_url', help='If this parameter is added, then the program will not provide an interactive QA session with the database.  Instead, the provided url will be downloaded and added to the database.')
args = parser.parse_args()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=args.loglevel.upper(),
    )

db = ArticleDB(args.db)

if args.add_url:
    db.add_url(args.add_url, recursive_depth=args.recursive_depth, allow_dupes=True)

else:
    while True:
        text = input('ragnews> ')
        if len(text.strip()) > 0:
            output = rag(text, db)
            print(output)