import os
import time
from groq import Groq, RateLimitError, InternalServerError
import requests

# https://console.groq.com/docs/rate-limits
# Requests Per Day (RPD)
request_limit = 14400
# Tokens Per Minute (TPM)  
token_limit = 18000    

class Groq_Wrapper:
    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )
        self.requests_remaining = request_limit
        self.tokens_remaining = token_limit
        self.request_reset_time = 0
        self.token_reset_time = 0

    def enforce_rate_limits(self):
        """
        Stall script if rate limits are hit 
        """
        if self.requests_remaining < 1:
            print(f"Requests used up! Sleeping for {self.request_reset_time} seconds.")
            time.sleep(self.request_reset_time)
            self.requests_remaining = request_limit
        
        if self.tokens_remaining < 1:
            print(f"Tokens used up! Sleeping for {self.token_reset_time} seconds.")
            time.sleep(self.token_reset_time)
            self.tokens_remaining = token_limit

    def str_time_to_seconds(self, time_str):
        """
        Converts time in str '1m5.583s' or '7.66s' to seconds as a float.
        """
        minutes = 0
        seconds = 0
        
        if 'm' in time_str:
            minutes_part, time_str = time_str.split('m')
            minutes = int(minutes_part)
        
        if 's' in time_str:
            seconds = float(time_str.replace('s', ''))
        
        return minutes * 60 + seconds

    def update_rate_limits_from_headers(self, headers):
        """
        Update rate limit information from API response headers.
        """
        self.requests_remaining = int(headers.get("x-ratelimit-remaining-requests", self.requests_remaining))
        self.tokens_remaining = int(headers.get("x-ratelimit-remaining-tokens", self.tokens_remaining))
        
        request_reset_time_str = headers.get("x-ratelimit-reset-requests", "0")
        token_reset_time_str = headers.get("x-ratelimit-reset-tokens", "0")
        
        self.request_reset_time = self.str_time_to_seconds(request_reset_time_str)
        self.token_reset_time = self.str_time_to_seconds(token_reset_time_str)

    def update_tokens_used(self, usage):
        """
        Update remaining tokens
        """
        self.tokens_remaining -= usage.prompt_tokens + usage.completion_tokens

    def summarize_chunk(self, chunk, max_retries=5, final_summary=False):
        """
        We need to call the split_document_into_chunks on text.
        Then for each paragraph in the output list,
        call the LLM code below to summarize it.
        Put the summary into a new list.
        Concatenate that new list into one smaller document.
        Recall the LLM code below on the new smaller document.
        """
        retries = 0
        while retries < max_retries:
            try:
                self.enforce_rate_limits()

                response = self.client.chat.completions.with_raw_response.create(
                    messages=[
                        {
                            'role': 'system',
                            'content': (
                                'Summarize the given text. '
                                'Limit the summary to 1 '
                                f'{["sentence", "5 sentence pargraph"][final_summary]}. '
                                'Just output the summary, do not return any commentary, remarks '
                                ', or other text.'
                            )
                        },
                        {
                            "role": "user",
                            "content": chunk,
                        }
                    ],
                    model="llama3-8b-8192",
                )
                
                completion = response.parse() 
                summary = completion.choices[0].message.content
                

                self.requests_remaining -= 1
                self.update_tokens_used(completion.usage)
                self.update_rate_limits_from_headers(response.headers)

                return summary
            
            except RateLimitError as rate_err:
                error_message = rate_err.args[0] if isinstance(rate_err.args[0], dict) else {}
                retry_after = error_message.get('error', {}).get('message', '').split('in ')[-1].split('s')[0]

                retry_after = float(retry_after) if retry_after else 10.0
                print(f"Rate limit exceeded. Sleeping for {retry_after} seconds.")
                time.sleep(retry_after)

                retries += 1
            
            except InternalServerError as internal_err:
                # Handle internal server error (503)
                print("Internal server error. Service is unavailable. Retrying in 10 seconds.")
                time.sleep(10)  # Wait for 10 seconds before retrying

                retries += 1

            except requests.exceptions.HTTPError as http_err:
                secs_to_sleep = int(http_err.response.headers.get('retry-after', 10))
                print(f"HTTP Error. Sleeping for {secs_to_sleep} seconds.")
                time.sleep(secs_to_sleep)

                retries += 1
                
        return ""

    def summarize_chunks(self, chunks, verbose=True):
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            summary = self.summarize_chunk(chunk)
            if verbose:
                print(f"Chunk {i} Summary")
                print(summary)
                print()
            chunk_summaries.append(summary)
        
        # Summarize the summaries
        final_summary = self.summarize_chunk(' '.join(chunk_summaries), final_summary=True)
        
        return final_summary