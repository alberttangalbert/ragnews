################################################################################
# rag
################################################################################


def rag(text, db):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.
    The db argument should be an instance of the `ArticleDB` class that contains the relevant documents to use.

    NOTE:
    There are no test cases because:
    1. the answers are non-deterministic (both because of the LLM and the database), and
    2. evaluating the quality of answers automatically is non-trivial.

    '''
    return text
    # FIXME:
    # Implement this function.
    # Recall that your RAG system should:
    # 1. Extract keywords from the text.
    # 2. Use those keywords to find articles related to the text.
    # 3. Construct a new user prompt that includes all of the articles and the original text.
    # 4. Pass the new prompt to the LLM and return the result.
    #
    # HINT:
    # You will also have to write your own system prompt to use with the LLM.
    # I needed a fairly long system prompt (about 15 lines) in order to get good results.
    # You can start with a basic system prompt right away just to check if things are working,
    # but don't spend a lot of time on the system prompt until you're sure everything else is working.
    # Then, you can iteratively add more commands into the system prompt to correct "bad" behavior you see in your program's output.


