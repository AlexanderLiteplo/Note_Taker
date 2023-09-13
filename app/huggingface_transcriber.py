from gradio_client import Client

class HuggingFaceTranscriber:
    def __init__(self, audio_files_path, transcripts_folder):
        print("HuggingFace Transcriber created")
        self.audio_files_path = audio_files_path
        self.transcripts_folder = transcripts_folder
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def transcribe(self, audio_file, censor_profanity=True):
        client = Client("https://matthijs-whisper-word-timestamps.hf.space/")
        result = client.predict(
                        self.audio_files_path + audio_file,	# str (filepath or URL to file) in 'Upload Audio' Audio component
                        "english",	# str (Option from: ['afrikaans', 'albanian', 'amharic', 'arabic', 'armenian', 'assamese', 'azerbaijani', 'bashkir', 'basque', 'belarusian', 'bengali', 'bosnian', 'breton', 'bulgarian', 'burmese', 'castilian', 'catalan', 'chinese', 'croatian', 'czech', 'danish', 'dutch', 'english', 'estonian', 'faroese', 'finnish', 'flemish', 'french', 'galician', 'georgian', 'german', 'greek', 'gujarati', 'haitian', 'haitian creole', 'hausa', 'hawaiian', 'hebrew', 'hindi', 'hungarian', 'icelandic', 'indonesian', 'italian', 'japanese', 'javanese', 'kannada', 'kazakh', 'khmer', 'korean', 'lao', 'latin', 'latvian', 'letzeburgesch', 'lingala', 'lithuanian', 'luxembourgish', 'macedonian', 'malagasy', 'malay', 'malayalam', 'maltese', 'maori', 'marathi', 'moldavian', 'moldovan', 'mongolian', 'myanmar', 'nepali', 'norwegian', 'nynorsk', 'occitan', 'panjabi', 'pashto', 'persian', 'polish', 'portuguese', 'punjabi', 'pushto', 'romanian', 'russian', 'sanskrit', 'serbian', 'shona', 'sindhi', 'sinhala', 'sinhalese', 'slovak', 'slovenian', 'somali', 'spanish', 'sundanese', 'swahili', 'swedish', 'tagalog', 'tajik', 'tamil', 'tatar', 'telugu', 'thai', 'tibetan', 'turkish', 'turkmen', 'ukrainian', 'urdu', 'uzbek', 'valencian', 'vietnamese', 'welsh', 'yiddish', 'yoruba']) in 'Language' Dropdown component
                        api_name="/predict"
        )
        print(result)
        

transcriber = HuggingFaceTranscriber("./audio_files/", "./transcripts")

transcriber.transcribe("test.mp3")