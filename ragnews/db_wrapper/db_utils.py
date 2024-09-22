import logging 
import re 
from datetime import datetime
from groq_wrapper.groq_wrapper import Groq_Wrapper

groq_wrapper = Groq_Wrapper()

def split_text(text, max_token_size):
    """
    Split the text into chunks with each chunk having no more than max_token_size tokens.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_chunk_size = 0
    
    for word in words:
        word_length = len(word)  # Approximate tokens by word length
        if current_chunk_size + word_length > max_token_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_chunk_size = word_length
        else:
            current_chunk.append(word)
            current_chunk_size += word_length
    
    # Add the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def summarize_text(text, seed=None):
    # split text into chunks 
    max_token_size = 5000
    chunks = split_text(text, max_token_size)
    summary = groq_wrapper.summarize_chunks(chunks, seed)
    return summary

def translate_text(text):
    system_prompt = (
        'You are a professional translator working for the United Nations. '
        'The following document is an important news article that needs to be translated into English. '
        'Provide a professional translation.'
    )
    user_prompt = text
    completion = groq_wrapper.query(system_prompt, user_prompt)
    parsed_completion = completion.parse() 
    translation = parsed_completion.choices[0].message.content
    return translation

def _logsql(sql):
    rex = re.compile(r'\W+')
    sql_dewhite = rex.sub(' ', sql)
    logging.debug(f'SQL: {sql_dewhite}')


def _catch_errors(func):
    '''
    This function is intended to be used as a decorator.
    It traps whatever errors the input function raises and logs the errors.
    We use this decorator on the add_urls method below to ensure that a webcrawl continues even if there are errors.
    '''
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.error(str(e))
    return inner_function

def parse_date(date_str):
    if not date_str:
        return None
    """
    Parses a date string, including those with timezone information.
    """
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"Date format not recognized: {date_str}")

def clean_string(s):
    return re.sub(r'[^a-zA-Z\s]', '', s)