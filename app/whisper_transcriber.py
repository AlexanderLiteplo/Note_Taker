import whisperx
import torch
import os
import json
import logging
from better_profanity import profanity

logging.basicConfig(level=logging.INFO)

SMALL_MODEL_SIZE = "small"
MEDIUM_MODEL_SIZE = "medium"
LARGE_MODEL_SIZE = "large"

class WhisperTranscriber:
    def __init__(self, audio_files_path, transcripts_folder):
        print("WhisperTranscriber created")
        self.audio_files_path = audio_files_path
        self.transcripts_folder = transcripts_folder
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def transcribe(self, audio_file, censor_profanity=True):
        # check if file exists
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
        
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
            
        model = whisperx.load_model(LARGE_MODEL_SIZE, device=device)
        result = model.transcribe(self.audio_files_path + audio_file)

        print(result["segments"]) # before alignment

        # load alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # align whisper output
        result_aligned = whisperx.align(result["segments"], model_a, metadata, self.audio_files_path + audio_file, device)

        print("Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["segments"]) # after alignment
        print("Word Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["word_segments"]) # after alignment 

        transcription = self.parse_transcription(result_aligned)
        
        transcription = self.clean_transcription(transcription, censor_profanity)
        
        transcription = self.ensure_transcription_has_text(transcription)
        
        self.store_transcription(audio_file, transcription)
        
        return transcription
    
    def ensure_transcription_has_text(self, transcription):
        if (len(transcription['word_segments']) == 0
            or len(transcription['segments']) == 0
            or len(transcription['segments']) < 3):
            transcription = None
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def clean_transcription(self, transcription, censor_profanity=True):
        for word_segment in transcription['word_segments']:
            
            if censor_profanity:
                first_letter = word_segment['text'][0]
                word_segment['text'] = profanity.censor(word_segment['text'])
                # replace the first letter with first_letter to make shit = s***
                word_segment['text'] = first_letter + word_segment['text'][1:]
            
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parse_transcription(self, result_aligned):
        transcription = {'word_segments': [],
                         'segments': []}
        
        for word_segment in result_aligned['word_segments']:
            new_word_segment = { 'text': word_segment['text'],  'start': word_segment['start'], 'end': word_segment['end']}
            transcription['word_segments'].append(new_word_segment)
            
        
        for segment in result_aligned['segments']:
            new_segment = { 'text': segment['text'],  'start': segment['start'], 'end': segment['end']}
            transcription['segments'].append(new_segment)
            
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def store_transcription(self, audio_file, result_aligned):
        with open(self.transcripts_folder + audio_file + ".json", "w+") as file:
            json.dump(result_aligned, file)

# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# root = "../../media_storage/"
# AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcript = transcriber.clean_transcription(transcriber.transcribe("vikings_(0, 46)_(1, 44).mp3"))
# print (transcript)