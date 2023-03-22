import os.path

import openai
from pydub import AudioSegment

filedir = "/Users/youfeng/Library"
# todo: get from upstream
filename = "/test.wav"
filepath = os.path.join(filedir, filename)


def get_file_size_MB(path):
    size = os.path.getsize(path)
    size = size / float(1024 * 1024)
    return round(size, 2)


shouldSplit = get_file_size_MB(filepath) > 25

if shouldSplit:
    file = AudioSegment.from_wav(filepath)

else:
    with open(filepath, "rb") as file:
        result = openai.Audio.transcribe("whisper-1", file)

