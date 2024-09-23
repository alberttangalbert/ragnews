#!/bin/bash

# Navigate to the ragnews folder
cd ../ragnews || exit

# Test cases for ragnews.db
queries_ragnews=(
  "tell me about the current presidential candidates"
  "who is projected to win the 2024 election?"
  "who is donald trump"
  "what are donald trump's policies?"
)

for query in "${queries_ragnews[@]}"; do
  echo "$query" | python3 chatbot.py --db=../sql_dbs/ragnews.db
done

# Test cases for claremont.db
queries_claremont=(
  "tell me about the claremont colleges"
  "which claremont college is the best for economics?"
  "what is the advantage of going to claremont mckenna over the other colleges?"
  "which claremont college has the highest tuition?"
)

for query in "${queries_claremont[@]}"; do
  echo "$query" | python3 chatbot.py --db=../sql_dbs/claremont.db
done