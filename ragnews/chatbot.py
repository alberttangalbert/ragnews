import argparse
import logging 
import sys 

from db_wrapper.articledb import ArticleDB
from ragnews.rag import rag_chatbot

def parse_arguments():
    '''
    Parses command-line arguments for the application.
    '''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loglevel', default='warning')
    parser.add_argument('--db', default='../sql_dbs/ragnews.db')
    parser.add_argument('--recursive_depth', default=0, type=int)
    parser.add_argument('--add_url', help='If this parameter is added, then the program will not provide an interactive QA session with the database.  Instead, the provided url will be downloaded and added to the database.')
    return parser.parse_args()

def setup_logging(loglevel):
    '''
    Configures the logging level and format.
    '''
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=loglevel.upper(),
    )

def main():
    args = parse_arguments()
    setup_logging(args.loglevel)

    try:
        db = ArticleDB(args.db)
    except Exception as e:
        logging.error(f"Failed to initialize the database: {e}")
        sys.exit(1)

    if args.add_url:
        try:
            db.add_url(args.add_url, recursive_depth=args.recursive_depth, allow_dupes=True)
            logging.info(f"Successfully added URL: {args.add_url}")
        except Exception as e:
            logging.error(f"Error adding URL to the database: {e}")
            sys.exit(1)
    else:
        # Check if input is from a pipe or interactive
        if sys.stdin.isatty():
            # Interactive q&a in terminal
            try:
                while True:
                    text = input('user_query> ')
                    if text.strip():
                        output = rag_chatbot(text, db)
                        print(output)
            except KeyboardInterrupt:
                print("\nExiting interactive session.")
            except Exception as e:
                logging.error(f"Error during interactive session: {e}")
                sys.exit(1)
        else:
            # Handle piped input
            try:
                text = sys.stdin.read().strip()
                if text:
                    output = rag_chatbot(text, db)
                    print(output)
            except Exception as e:
                logging.error(f"Error handling piped input: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()