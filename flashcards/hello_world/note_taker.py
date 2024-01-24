from nltk.tokenize import word_tokenize
from .flashcard_maker import FlashCardMaker
import os
from .openai_transcriber import OpenAITranscriber
from flashcards.hello_world.openai_api import OpenaiApi
import logging
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)


class note_taker:
    def __init__(self):
        print("Note Taker initialized")
        self.AUDIO_FILES_PATH = "./temp/"
        self.TRANSCRIPTS_FOLDER = "./transcripts/"
        self.NOTES_FOLDER = "./notes/"
        self.MAX_TOKENS = 4096

    def convert_m4a_to_mp3(m4a_path, mp3_path):
        audio = AudioSegment.from_file(m4a_path, format="m4a")
        audio.export(mp3_path, format="mp3")

    def convert_mp4_to_mp3(mp4_path, mp3_path):
        audio = AudioSegment.from_file(mp4_path, format="mp4")
        audio.export(mp3_path, format="mp3")

    def split_transcript(transcript):
        tokens = word_tokenize(transcript)
        
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

    def make_notes(self):
        # Create the transcriber and API objects
        logging.info("Creating transcriber and API objects...")
        transcriber = OpenAITranscriber(self.AUDIO_FILES_PATH, self.TRANSCRIPTS_FOLDER)
        api = OpenaiApi()

        # Convert all m4a files to mp3
        for filename in os.listdir(self.AUDIO_FILES_PATH):
            if filename.endswith(".m4a"):
                convert_m4a_to_mp3(f"{self.AUDIO_FILES_PATH}/{filename}", f"{self.AUDIO_FILES_PATH}/{filename[:-4]}.mp3")
                
        # convert all mp4 files to mp3
        for filename in os.listdir(self.AUDIO_FILES_PATH):
            if filename.endswith(".mp4"):
                convert_mp4_to_mp3(f"{self.AUDIO_FILES_PATH}/{filename}", f"{self.AUDIO_FILES_PATH}/{filename[:-4]}.mp3")

        # Iterate over the files in the repository
        for filename in os.listdir(self.AUDIO_FILES_PATH):
            if filename.endswith(".mp3"):  # Or whatever format your audio files are in
                # Transcribe the audio file
                transcript = transcriber.transcribe(filename)
                transcript_text = transcript
                
                # If transcript is too long, split it
                chunks = split_transcript(transcript_text)
                
                all_notes = ""
                # Pass each chunk to GPT and save the notes
                for i, chunk in enumerate(chunks):
                    system_prompt = "You are the world's best lecture notes taker. You will be passed in a transcript from a part of a lecture and you have to take nicely formatted notes on it. Use lot's of emojis and beautiful formatting. Ensure every single line has at least one emoji. The transcript may have errors so use your best judgement."
                    prompt = "Please take nicely formatted notes on the following lecture transcript:\n\n" + chunk
                    notes = api.query(system_prompt, prompt, "gpt-3.5-turbo")  # Fill in user_prompt and model as needed
                    
                    logging.info(notes)
                
                    # Concatenate the notes
                    all_notes += notes + "\n"
                    
                # Save all notes to a single .txt file
                with open(f"{self.NOTES_FOLDER}{filename[:-4]}.txt", 'w') as file:
                    file.write(all_notes)

        # go through notes folder, for each file, create flashcards
        flashcard_maker = FlashCardMaker()
        for filename in os.listdir(self.NOTES_FOLDER):
            if filename.endswith(".txt"):
                with open(f"{self.NOTES_FOLDER}{filename}", 'r') as file:
                    notes = file.read()
                    flashcards = flashcard_maker.generate_flashcards_from_text(notes)
                    
                    with open(f"{self.NOTES_FOLDER}{filename[:-4]}.json", 'w') as file:
                        file.write(flashcards)
                    
                    print(f"Saved to {self.NOTES_FOLDER}{filename[:-4]}.json")




