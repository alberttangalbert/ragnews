from groq_wrapper.groq_wrapper import Groq_Wrapper
from .rag_utils import find_answer_in_brackets

groq_wrapper = Groq_Wrapper()

def extract_keywords_masked(text, max_tries=5):
    r'''
    This is a helper function for RAG on masked text.
    Given an input text,
    this function extracts the keywords that will be used to perform the search for articles that will be used in RAG.

    >>> extract_keywords('Who is the current democratic presidential nominee?', seed=0)
    'Democratic presidential nominee,2020 United States presidential election,Joe Biden,Kamala Harris,Democratic Party'
    >>> extract_keywords('What is the policy position of Trump related to illegal Mexican immigrants?', seed=0)
    'Donald Trump,Mexican immigrants,illegal immigration,border wall,deportation'

    Note that the examples above are passing in a seed value for deterministic results.
    In production, you probably do not want to specify the seed.
    '''
    system_prompt = (
        'You are given a fill-in-the-blank question that containing a masked value [MASK0]. '
        'Your job is to generate 3 Google search queries based on the given fill-in-the-blank question '
        'that will help someone else find the value for [MASK0]. '
        'Make sure the queries will not lead someone to the wrong answer! '
        'Respond with only ONE LINE where each keyword is separated by a comma.'
    )
    user_prompt = (
        'Fill-in-the-blank question:\n'
        f'{text}'
    )
    attempts = 0
    while attempts < max_tries:
        try:
            completion = groq_wrapper.query(system_prompt, user_prompt)
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

def rag_masked(text, db, max_tries=5, articles_limit=3):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.
    The db argument should be an instance of the `ArticleDB` class that contains the relevant documents to use.


    NOTE:
    There are no test cases because:
    1. the answers are non-deterministic (both because of the LLM and the database), and
    2. evaluating the quality of answers automatically is non-trivial.

    '''
    # 1. Extract keywords from the text.
    keywords = extract_keywords_masked(text)

    # 2. Use those keywords to find articles related to the text.
    articles = db.find_articles(keywords, limit=articles_limit)

    if not articles:
        return "No relevant articles found."
    
    # 3. Construct a new user prompt that includes all of the articles and the original text.
    system_prompt = (
        f"Your job is to find one word that replaces [MASK0] in the given fill-in-the-blank question.\n"
        "Think about if your response is logical.\n"
        "Answer with one word in square brackets "
        "then explain where you found that answer. "
        "If the answer is a name then return only the last name.\n\n"
        f"Given fill-in-the-blank question:\n{text}"
    )

    user_prompt = "Provided Articles:\n"
    for i, article in enumerate(articles):
        user_prompt += f"ARTICLE{i+1}. Title: {article['title']}\nSummary: {article['en_summary']}\n\n"

    # 4. Pass the new prompt to the LLM and return the result.
    attempts = 0
    while attempts < max_tries:
        try:
            completion = groq_wrapper.query(
                system_prompt=system_prompt, 
                user_prompt=user_prompt
            )
            parsed_completion = completion.parse() 
            response = parsed_completion.choices[0].message.content

            # if there is one word return without square brackets
            if len(response.split()) == 1:
                return response
            # if the response contains the word inside square brackets 
            answer = find_answer_in_brackets(response)
            if answer:
                # make sure there aren't multiple words in the bracket 
                if len(answer.split()) > 1:
                    raise ValueError("Only one word should be found")
                return answer
            else:
                raise ValueError("No answer found!")
        except Exception:
            attempts += 1
    return ""