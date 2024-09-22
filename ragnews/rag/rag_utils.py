import re

def find_answer_in_brackets(text):
    # match content inside square brackets
    pattern = r"\[(.*?)\]"
    matches = re.finditer(pattern, text)
    
    # find first match that doesn't contain "mask"
    for match in matches:
        content = match.group(1)
        if "mask" not in content.lower(): 
            return content
    return None 