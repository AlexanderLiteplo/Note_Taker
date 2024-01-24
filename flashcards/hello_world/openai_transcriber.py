import time
import json
import openai
import os
from pydub import AudioSegment
import logging

logging.basicConfig(level=logging.INFO)

class OpenAITranscriber:
    def __init__(self, audio_files_path, transcripts_folder):
        self.audio_files_path = audio_files_path
        self.transcripts_folder = transcripts_folder
    
    def get_api_key(self):
        file_path = "../../OPENAI_API_KEY.txt"  # path to the file with the API key
        try:
            with open(file_path, 'r') as file:
                api_key = file.readline().strip()  # Read the first line and remove any leading/trailing white spaces
            return api_key
        except FileNotFoundError:
            print(f"API key file not found at {file_path}")
            return None
    
    def convert_m4a_to_mp3(self, m4a_path, mp3_path):
        # Load m4a file
        audio = AudioSegment.from_file(m4a_path, format="m4a")

        # Export as mp3
        audio.export(mp3_path, format="mp3")
    
    def transcribe(self, audio_file):
        if not os.path.exists(self.audio_files_path + audio_file):
            logging.info(f"Audio file {audio_file} does not exist")
            raise Exception('Audio file does not exist')
        else:
            print("Audio file found, transcribing...")
            
        # check if json file exists
        if os.path.exists(self.transcripts_folder + audio_file + ".json"):
            print("JSON file found, loading...")
            with open(self.transcripts_folder + audio_file + ".json", "r") as f:
                transcription = json.load(f)
            return transcription
        
        start_time = time.time()
        openai.api_key = self.get_api_key()
        audio_path = self.audio_files_path + audio_file
        json_path = self.transcripts_folder + audio_file[:-4] + ".json"
        
        if audio_file.endswith(".m4a"):
            self.convert_m4a_to_mp3(audio_path, audio_path[:-4] + ".mp3")

        audio_path = self.audio_files_path + audio_file[:-4] + ".mp3"
        
        transcript_data = ""
        # Check if the audio file exists
        if not os.path.isfile(audio_path):
            raise Exception(f"Audio file does not exist: {audio_path}")

        # Load audio file
        audio = AudioSegment.from_mp3(audio_path)

        # Set the duration of each chunk
        chunk_length = 10 * 60 * 1000  # in milliseconds

        # Split audio file into chunks and transcribe each chunk
        for i in range(0, len(audio), chunk_length):
            chunk_start_time = time.time()
            # Create chunk
            audio_chunk = audio[i:i + chunk_length]
            
            # Save chunk to a temporary file
            temp_path = "/tmp/chunk.mp3"
            audio_chunk.export(temp_path, format="mp3")

            # Transcribe the audio chunk
            with open(temp_path, "rb") as chunk_file:
                transcript = openai.Audio.transcribe("whisper-1", chunk_file)
                transcript_data = transcript_data + " " +  transcript['text']
            
            chunk_end_time = time.time()
            print(transcript)
            print(f"Chunk {i // chunk_length} took {chunk_end_time - chunk_start_time} seconds")

        print(transcript_data)
        
        # Save transcript data to a JSON file
        with open(json_path, 'w') as json_file:
            json.dump(transcript_data, json_file)
        
        end_time = time.time()
        
        print(f"Transcription took {end_time - start_time} seconds")
        
        return transcript_data

# transcriber = OpenAITranscriber("./audio_files/", "./transcripts/")

# transcriber.transcribe("New Recording 9.m4a")