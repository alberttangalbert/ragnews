# ragnews ![](https://github.com/alberttangalbert/ragnews/actions/workflows/tests.yml/badge.svg)

Performs RAG on sql database (.db) files. 
User input prompts are ran through the RAG to fetch relevant articles in the database.
The user will input the path of the sql database file as one of the arguments. 
The summaries of the articles are then passed into a Groq wrapper.
Groq then responds with given the updated information from the articles. 

Steps to setup:
1) Create .env file (example given) and enter GROQ api key
2) pip install -r requirements.txt
3) Clone metahtml repository 
```
$ git clone --filter=blob:none --no-checkout https://github.com/mikeizbicki/metahtml
$ cd metahtml
$ git sparse-checkout init
$ git sparse-checkout set --cone
$ echo '/*' > .git/info/sparse-checkout
$ echo '!/tests/.cache/' >> .git/info/sparse-checkout
$ git sparse-checkout reapply
$ git checkout master
```

4) Clone bunch repository 
```
$ git clone https://github.com/alberttangalbert/bunch.git
$ cd bunch
$ pip install .
```

4) Export .env variables to environment
```
$ export $(cat .env)
```

5) Run to create/update existing sql database (optional)
```
$ cd ragnews 
$ python3 run.py python3 run.py --add_url="$url" --recursive_depth="$depth" --db="$path_to_db"
```

Chat with Groq that has RAG capabilities 
```
$ python3 run.py python3 run.py --db="$path_to_db"
```

Note: To exit, press ctrl+Z

Example runs:

---
```
$ python3 run.py
$ ragnews> who is the current presidential candidate
The current presidential candidates are:

1. Vice President Kamala Harris (Democrat)
2. Former President Donald Trump (Republican)

They are scheduled to face off in their first and potentially only debate on Tuesday night in Philadelphia.

Note: As of the knowledge cutoff, President Joe Biden had withdrawn from the race after a disappointing performance in the first general election debate. However, the information provided in the articles suggests that the primary candidates are currently Vice President Kamala Harris and former President Donald Trump.
```
---
```
$ python run.py --db="./sql_dbs/claremont.db"
$ user_query> tell me about claremont mckenna college
Claremont McKenna College (CMC) is a private liberal arts college located in Claremont, California, United States. It is one of the seven member institutions of The Claremont Colleges, a network of liberal arts colleges and graduate schools. CMC is known for its strong programs in the social sciences, humanities, and natural sciences, as well as its focus on leadership, international relations, and global issues.

Here are some key facts about Claremont McKenna College:

1. History: CMC was founded in 1946 as Claremont Men's College, and it was the first college in the Claremont Colleges group. The college became co-educational in 1976.
2. Academics: CMC offers undergraduate and graduate degrees in a wide range of fields, including economics, international relations, history, literature, philosophy, and the sciences. The college is known for its strong programs in politics, policy, and international relations.
3. Student body: CMC has a student body of around 1,300 students, with a student-faculty ratio of 7:1. The college has a diverse student body, with students from all 50 states and over 60 countries.
4. Faculty: CMC has a faculty of around 100 full-time professors, many of whom are leading scholars in their fields. The college also has a number of visiting professors and lecturers who come from around the world to teach and conduct research.
5. Campus: CMC's campus is located in the heart of Claremont, a small city about 35 miles east of Los Angeles. The college owns a number of buildings in Claremont, including the iconic Kravis Center, which serves as the college's main administrative and academic building.
6. Athletics: CMC is a member of the Southern California Intercollegiate Athletic Conference (SCIAC) and has a number of varsity sports teams, including soccer, basketball, tennis, and volleyball.
7. Location: Claremont is located in the San Gabriel Valley, about 35 miles east of downtown Los Angeles. The city has a small-town feel, with a number of shops, restaurants, and cultural attractions.
8. Community: CMC has a strong sense of community, with a number of student clubs, organizations, and volunteer opportunities. The college is also active in the local community, with a number of partnerships with nearby schools and organizations.
9. Internships and jobs: CMC has a strong career services program, with a number of internship and job opportunities available to students. The college also has a number of career advisors who work with students to help them find jobs and internships.
10. Rankings: CMC is highly regarded and has been ranked highly by a number of national publications. In 2022, U.S. News & World Report ranked CMC #22 among national liberal arts colleges.

Related articles:

* Racial diversity among P-P, CMS athletes not reflective of student bodies - The Student Life
* Long before his NBA titles, Spurs coach Gregg Popovich says he 'fell in love' with Division III lifestyle at Pomona-Pitzer
* From Walk-On To National Champion: Tyra Abraham On Her Running Career That Almost Wasn't - The Student Life 
```
---
```
$ python run.py --db="./sql_dbs/ragnews.db"  
$ user_query> who is projected to win the 2024 election
As of the articles provided, it appears that the outcome of the 2024 presidential election is uncertain and subject to various factors. There is no clear projection or prediction of which candidate, Kamala Harris or Donald Trump, is likely to win.

However, it's worth noting that the articles highlight the tight race for control of Congress, with Democrats gaining energy and enthusiasm among voters, potentially impacting the outcome of the election. Additionally, the debate performance of the candidates, as well as their campaign strategies and public perception, may play a crucial role in shaping the outcome of the election.

It's also important to consider that the articles are citing various factors that can influence the election outcome, such as:

1. The importance of debates: The articles highlight the significance of the debate, suggesting that Harris and Trump's performances may have a measurable impact on the election.
2. Voter turnout: The articles mention the potential for high voter turnout, which could skew the outcome in one direction or the other.
3. Campaign messaging: The articles discuss the candidates' focus on specific issues, such as immigration, abortion, and worker wages, which may resonate with different segments of the electorate.
4. Fundraising: The articles mention the Democratic Party's fundraising advantage, which could impact their ability to mobilize voters and resources.

Given the complexities involved, it's challenging to project a clear winner at this point. It's essential to stay updated with the latest developments, candidate performances, and public opinion surveys to gain a better understanding of the election's outcome.
```






