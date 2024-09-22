from groq_wrapper.groq_wrapper import Groq_Wrapper

groq_wrapper = Groq_Wrapper()

def extract_keywords(text, max_tries=3):
    r'''
    This is a helper function for RAG.
    Given an input text,
    this function extracts the keywords that will be used to perform the search for articles that will be used in RAG.

    >>> extract_keywords('Who is the current democratic presidential nominee?', seed=0)
    'Joe, candidate, nominee, presidential Democrat, election primary, TBD voting politics'
    >>> extract_keywords('What is the policy position of Trump related to illegal Mexican immigrants?', seed=0)
    'Trump, Mexican immigrants policy position, illegal, border control, deportation, walls'

    Note that the examples above are passing in a seed value for deterministic results.
    In production, you probably do not want to specify the seed.
    '''
    system_prompt = (
        'Generate 5 key phrases based on the given query. These keywords should lead the user '
        'to articles with answers if they entered them in a Google search. '
        'Respond with only one line where each keyword is separated by a comma.'
    )

    attempts = 0
    while attempts < max_tries:
        try:
            completion = groq_wrapper.query(system_prompt, text)
            parsed_completion = completion.parse()
            keywords = parsed_completion.choices[0].message.content.strip()

            # Ensure the response follows the expected format (comma-separated keywords)
            if not keywords or "," not in keywords:
                raise ValueError("Unexpected response format. Expected comma-separated keywords.")
            # Ensure the response is only one line
            elif "\n" in keywords:
                raise ValueError("There should only be one line returned!")
            else:
                return ",".join([kw.strip() for kw in keywords.split(",")])

        except (AttributeError, KeyError, IndexError, ValueError) as e:
            attempts += 1
        except Exception:
            attempts += 1
        attempts += 1
    print(f"Could not extract valid keywords from query.")
    return ""

def rag_chatbot(text, db):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.
    The db argument should be an instance of the `ArticleDB` class that contains the relevant documents to use.

    NOTE:
    There are no test cases because:
    1. the answers are non-deterministic (both because of the LLM and the database), and
    2. evaluating the quality of answers automatically is non-trivial.

    '''
    # 1. Extract keywords from the text.
    keywords = extract_keywords(text)

    # 2. Use those keywords to find articles related to the text.
    articles = db.find_articles(keywords)

    if not articles:
        return "No relevant articles found."
    
    # 3. Construct a new user prompt that includes all of the articles and the original text.
    prompt = f"User question: {text}\n\nRelated Articles:\n"
    for i, article in enumerate(articles):
        prompt += f"ARTICLE{i+1}. Title: {article['title']}\nSummary: {article['en_summary']}\n\n"
    prompt += "Based on the above user question and related articles, generate a helpful response."
    
    # 4. Pass the new prompt to the LLM and return the result.
    completion = groq_wrapper.query(prompt, text)
    parsed_completion = completion.parse() 
    response = parsed_completion.choices[0].message.content
    return response

