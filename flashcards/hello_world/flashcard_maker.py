import openai
from nltk.tokenize import word_tokenize
import logging
import os
import json

logging.basicConfig(level=logging.INFO)
class FlashCardMaker:
    def __init__(self, api_key):
        self.api_key = api_key
        print("FlashCardMaker initialized")
        
    def create_flashcards(self, text):
        flashcards = []
        chunks = self.chunk_text(text)
        for chunk in chunks:
            flashcards.append(self.generate_flashcards_from_text(chunk))
        return flashcards
        
    def chunk_text(self, text):
        tokens = word_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_token_count = 0
        for token in tokens:
            if current_token_count + len(token) > 4096:
                # If adding the next token would exceed the limit, we start a new chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = [token]
                current_token_count = len(token)
            else:
                # Otherwise, we add the token to the current chunk
                current_chunk.append(token)
                current_token_count += len(token)
        
        # Don't forget to add the last chunk if it's non-empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def generate_flashcards_from_text(self, text):
        openai.api_key = self.api_key
        
        flashcards = None
        max_attempts = 10
        num_attempts = 0

        while not flashcards and num_attempts < max_attempts:
            logging.info(f"Attempt {num_attempts + 1} of {max_attempts}")
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a flashcard text maker. 
                    You are given a text and you must make flashcards for it of any memorizable concepts or facts.
                    You must reply in only json format with a list of flashcards.
                    Flashcards must be of the format: {"term": "front of card", "definition": "back of card"}.
                    The list should be of the format: {"card_list": [{"term": "front of card", "definition": "back of card"}, ...]}
                    Reply with the json list and nothing else.
                        """},
                    {"role": "user", "content": f"""Here is the text to make json flashcards for: {text}"""}
                ]
            )

            logging.info(f"Response: {response['choices'][0]['message']['content']}")

            # Extract flashcards_json from the response message content
            flashcards_json = response['choices'][0]['message']['content']
            
            # Ensure that the flashcards are in the correct format
            try:
                logging.info(f"Attempting to load json data")
                flashcards_data = json.loads(flashcards_json)  # Load json data
                
                if 'card_list' not in flashcards_data:
                    flashcards = None
                    logging.info("card_list key not found in flashcards_data")
                elif not isinstance(flashcards_data['card_list'], list):
                    flashcards = None
                    logging.info("'card_list' is not a list")
                else:
                    flashcards = flashcards_data['card_list']
                    for card in flashcards:
                        if not isinstance(card, dict) or "term" not in card or "definition" not in card:
                            flashcards = None
                            logging.info("Flashcards is not a list of dictionaries with the keys 'term' and 'definition'")
                            break
            except ValueError as e:
                flashcards = None
                logging.info(f"Flashcards data is not a valid JSON object: {e}")
            
            num_attempts += 1

        return flashcards