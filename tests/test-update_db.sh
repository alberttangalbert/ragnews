#!/bin/bash

# Navigate to the ragnews folder
cd ../ragnews || exit

testing_urls='
https://apnews.com/hub/donald-trump
https://apnews.com/hub/kamala-harris
'

for url in $testing_urls; do
    echo url
    python3 run.py --add_url="$url" --recursive_depth=1 --db=./sql_dbs/ragnews.db --loglevel=DEBUG
done