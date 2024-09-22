#!/bin/bash

# Navigate to the ragnews folder
cd ../ragnews || exit

testing_urls='
https://tsl.news/
https://www.claremontindependent.com/
'
for url in $testing_urls; do
    echo url
    python3 chatbot.py --add_url="$url" --recursive_depth=3 --db=./sql_dbs/ragnews.db --loglevel=INFO
done
