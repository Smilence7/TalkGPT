import os.path
import copy
import openai
import logging
from pydub import AudioSegment


def get_file_size_MB(path):
    size = os.path.getsize(path)
    size = size / float(1024 * 1024)
    return round(size, 2)


def _trimmed_fetch_response(logger, resp, n):
    if n == 1:
        return resp['choices'][0]['message']['content'].strip()
    else:
        logger.debug('_trimmed_fetch_response :: returning {0} responses from GPT-3'.format(n))
        texts = []
        for idx in range(0, n):
            texts.append(resp['choices'][idx]['message']['content'].strip())
        return texts


class S2TConverter:

    def __init__(self, file_meta):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_meta = file_meta
        self.response = None

    def convert(self):
        self.logger.info(self.file_meta['path'])
        should_split = get_file_size_MB(self.file_meta['path']) > 25
        if should_split:
            file = AudioSegment.from_wav(self.file_meta['path'])
            self.response = openai.Audio.transcribe("whisper-1", file)
        else:
            with open(self.file_meta['path'], "rb") as file:
                self.response = openai.Audio.transcribe("whisper-1", file)
        self.logger.info(self.response['text'])
        return self.response['text']
        # todo: save to file temporarily


class ChatService:
    def __init__(self, model="gpt-3.5-turbo", temperature=1, top_p=1, n=1, max_tokens=100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.n = n
        self.max_tokens = max_tokens
        self.prompt = [
            {"role": "system", "content: ": "You are a helpful assistant with ability of language improving like "
                                            "showing more native expression of speech. You should provide the "
                                            "polished version of the given speech directly, while trying to "
                                            "maintain the original meaning as much as possible."},
            {"role": "user", "content": "I like table games, i also like foreign cultures."},
            {"role": "assistant", "content": "I enjoy playing tabletop games and have a fascination with foreign "
                                             "cultures."}
        ]

    def query(self, user_in):
        query = {"role": "user", "content": "{0}".format(user_in)}
        messages = copy.deepcopy(self.prompt).append(query)
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            max_tokens=self.max_tokens,
        )
        return _trimmed_fetch_response(self.logger, resp, self.n)
