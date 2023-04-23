import logging.config
import os.path
import threading
import time
import wave
from service import S2TConverter, ChatService, T2SConverter, ContextGenerator, play
import pyaudio
import openai
from pynput import keyboard
import sys


class Recorder:

    def __init__(self, p, dir_path, chunk_size=1024, sample_rate=44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.p = p
        self.stream = None
        self.frames = []
        self.running = True
        self.dir_path = dir_path
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.num_read_channel = 1
        self.num_write_channel = 1
        self.lock = threading.Lock()

    def record(self):
        self.logger.info("Start recording...")

        self.open_stream()
        while self.running:
            try:
                data = self.stream.read(self.chunk_size)
                self.frames.append(data)
            except IOError:
                self.logger.error("IOError")
        self.close_stream()

    def stop_gracefully(self):
        self.logger.info("Stop recording...")
        self.running = False

    def stop_now(self):
        self.logger.info("Stop recording...")
        self.close_stream()

    def open_stream(self):
        with self.lock:
            self.running = True
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=self.num_read_channel,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def close_stream(self):
        with self.lock:
            self.running = False
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def save(self, filename):
        if not self.frames:
            self.logger.warning("Error occurred when saving, frames content is empty.")
            return
        if filename is None:
            self.logger.error("Error occurred when saving, filename is null.")
            return
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path, 0o755)
        fullname = os.path.join(self.dir_path, filename)
        wf = wave.open(fullname, 'wb')
        wf.setnchannels(self.num_write_channel)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.frames = []
        return {
            'name': filename,
            'dir': self.dir_path,
            'path': fullname,
            'size': len(self.frames)
        }


class Producer(threading.Thread):

    def __init__(self, config, queue):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dir_path = config['save_dir']
        self.config = config
        self._hot_key = config['hot_key']
        self.queue = queue
        self.p = pyaudio.PyAudio()
        self.recorder = None
        self.pressing = False
        self.filename = None
        self.recorder_threads = []
        self.idx = -1

    @property
    def hot_key(self):
        return self._hot_key

    @hot_key.setter
    def hot_key(self, value):
        self._hot_key = value

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char(self.hot_key) and not self.pressing:
            self.pressing = True
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            self.filename = f'rec-{timestamp}.wav'
            self.recorder = Recorder(self.p, self.dir_path)
            self.recorder_threads.append(threading.Thread(target=self.recorder.record))
            self.idx += 1
            self.recorder_threads[self.idx].start()
            self.logger.debug(self.recorder_threads[self.idx].getName() + " started")

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char(self.hot_key) and self.pressing:
            self.pressing = False
            self.recorder.stop_gracefully()
            self.recorder_threads[self.idx].join()
            file = self.recorder.save(self.filename)
            if file is not None:
                self.queue.put(file)

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            self.logger.info("Start listening...")
            listener.join()
        self.logger.info("End listening...")


class Consumer(threading.Thread):
    def __init__(self, config, queue):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.queue = queue
        self.running = True
        self.worker = Worker(self.config)

    def run(self):
        while self.running:
            file_meta = self.queue.get()
            self.worker.run(file_meta)
            self.queue.task_done()


class Worker:
    def __init__(self, config):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.save_dir = config['save_dir']
        if openai.api_key is None:
            openai.api_key = config['api_key']['openai']
        self.s2t = S2TConverter()
        self.generator = ContextGenerator(config['gpt']['mode'])
        self.chatbot = ChatService(model=config['gpt']['model'])
        self.t2s = T2SConverter(config)

    def run(self, file_meta):
        try:
            text = self.s2t.convert(file_meta['path'])
            self.logger.info("User: {0}".format(text))
            text = self.generator.generate(text)
            text = self.chatbot.chat(text)
            self.generator.update_response(text)
            self.logger.info("TalkGPT: {0}".format(text))
            save_path = os.path.join(os.path.normpath(self.save_dir), file_meta['name'].split('.')[0] + '-reply.mp3')
            self.t2s.convert_and_save(text, save_path)
            play(save_path)
        except ValueError as e:
            self.logger.error("Error in speech-to-text: {0}".format(e))
            sys.exit(-1)
