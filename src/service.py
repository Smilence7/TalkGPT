import os.path
import copy
import openai
import logging
import sys
from botocore.exceptions import BotoCoreError, ClientError
import boto3
from contextlib import closing
import pydub.playback
from pydub import AudioSegment
from playsound import playsound


def get_file_size_MB(path):
    size = os.path.getsize(path)
    size = size / float(1024 * 1024)
    return round(size, 2)


def play(path):
    playsound(path)


def play_bytes(data):
    # todo: install ffmpeg and test
    audio_seg = AudioSegment(
        data=data,
        sample_width=1,
        frame_rate=44100,
        channels=1
    )
    pydub.playback.play(audio_seg)


def _trimmed_fetch_response(logger, resp, n):
    if n == 1:
        return resp.choices[0].message.content.strip()
    else:
        logger.debug('_trimmed_fetch_response :: returning {0} responses from GPT-3'.format(n))
        texts = []
        for idx in range(0, n):
            texts.append(resp.choices[0].message.content.strip())
        return texts


class S2TConverter:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def convert(self, audio_path):
        if audio_path is None or audio_path == "":
            msg = "audio_path is empty"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.info("Converting speech to text: {0}".format(audio_path))
        should_split = get_file_size_MB(audio_path) > 25
        if should_split:
            file = AudioSegment.from_wav(audio_path)
            response = openai.Audio.transcribe("whisper-1", file)
        else:
            with open(audio_path, "rb") as file:
                response = openai.Audio.transcribe("whisper-1", file)
        self.logger.debug(response)
        self.logger.info("Speech to text result: {0}".format(response['text']))
        return response['text']
        # todo: save to file temporarily


class ChatService:
    def __init__(self, model="gpt-3.5-turbo", temperature=1, top_p=1, n=1, max_tokens=100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.n = n
        self.max_tokens = max_tokens

    def query(self, req):
        if req is None or req == '':
            msg = "request is none or empty."
            self.logger.error(msg)
            raise ValueError(msg)
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=req,
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            max_tokens=self.max_tokens,
        )
        self.logger.debug("Response: {0}".format(resp))
        return _trimmed_fetch_response(self.logger, resp, self.n)


class T2SConverter:
    def __init__(self, config, save_path):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.save_dir = config['save_dir']
        self.client = boto3.Session(
            aws_access_key_id=config['api_key']['aws']['key_id'],
            aws_secret_access_key=config['api_key']['aws']['key'],
            region_name=config['polly']['region_name']).client('polly')
        self.voice_id = config['polly']['voice_id']
        self.output_format = config['polly']['output_format']
        self.save_path = save_path

    def convert(self, text):
        if text is None or text == '':
            msg = "text is none or empty"
            self.logger.error(msg)
            raise ValueError(msg)
        try:
            speech = self.client.synthesize_speech(
                Text=text,
                VoiceId=self.voice_id,
                OutputFormat=self.output_format)
        except (BotoCoreError, ClientError) as e:
            self.logger.error(e)
            sys.exit(-1)
        return speech

    def save(self, speech):
        if speech is None:
            msg = "speech is none"
            self.logger.error(msg)
            raise ValueError(msg)
        if "AudioStream" in speech:
            with closing(speech["AudioStream"]) as stream:
                self.logger.info('Audio content saving to file "{0}"'.format(self.save_path))
                try:
                    data = stream.read()
                    with open(self.save_path, "wb") as file:
                        file.write(data)
                except IOError as e:
                    self.logger.error(e)
                    sys.exit(-1)
        else:
            self.logger.error("Could not stream audio")
            sys.exit(-1)
        return data

    def convert_and_save(self, text):
        speech = self.convert(text)
        self.save(speech)

    def convert_and_get(self, text):
        speech = self.convert(text)
        return self.save(speech)


class Generator:
    def __init__(self, key):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.key = key
        self.prompts = {
            "polish": [
                {"role": "system", "content": "You are a helpful assistant with ability of language improving like "
                                              "showing more native expression of speech. You should provide the "
                                              "polished version of the given speech directly, while trying to "
                                              "maintain the original meaning as much as possible."},
                {"role": "user", "content": "I like table games, i also like foreign cultures."},
                {"role": "assistant", "content": "I enjoy playing tabletop games and have a fascination with foreign "
                                                 "cultures."}
            ]
        }

    def generate(self, raw):
        if raw is None or raw == '':
            msg = "raw is none or empty"
            self.logger.error(msg)
            raise ValueError(msg)
        if self.key == "polish":
            query = {"role": "user", "content": "{0}".format(raw)}
            self.logger.info('query :: {0}'.format(query))
            messages = copy.deepcopy(self.prompts[self.key])
            messages.append(query)
            return messages
        else:
            self.logger.debug("Using free talking mode.")
            return raw

