import os.path
import threading
import openai
from pydub import AudioSegment

openai.api_key = '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'

def get_file_size_MB(path):
    size = os.path.getsize(path)
    size = size / float(1024 * 1024)
    return round(size, 2)


class S2TConverter(threading.Thread):
    def __init__(self, file_meta):
        super().__init__()
        self.file_meta = file_meta
        self.response = None

    def convert(self):
        should_split = get_file_size_MB(self.file_meta['path']) > 25
        if should_split:
            file = AudioSegment.from_wav(self.file_meta['path'])
            self.response = openai.Audio.transcribe("whisper-1", file)
            # todo: check API
        else:
            with open(self.file_meta['path'], "rb") as file:
                self.response = openai.Audio.transcribe("whisper-1", file)
        print(self.response['text'])
        # todo: save to file temporarily

    def run(self):
        print(self.file_meta['path'])
        self.convert()
