import os.path
import queue
import threading
import time
import wave
from converter import S2TConverter

import pyaudio
from pyaudio import Stream
from pynput import keyboard


class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


@Singleton
class Recorder:
    running = True
    p = pyaudio.PyAudio()
    frames = []
    filepath = './saved/record'
    chunk_size = 1024
    sample_rate = 44100
    num_read_channel = 1
    num_write_channel = 1
    stream = p.open(format=pyaudio.paInt16,
                    channels=num_read_channel,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    def __init__(self, chunk_size=1024, sample_rate=44100):
        pass

    @classmethod
    def record(cls):
        while cls.running:
            data = cls.stream.read(1024)
            cls.frames.append(data)
        cls.stream.stop_stream()
        cls.stream.close()

    @classmethod
    def stopGracefully(cls):
        cls.running = False

    @classmethod
    def stopNow(cls):
        cls.running = False
        time.sleep(1)
        cls.stream.stop_stream()
        cls.stream.close()

    @classmethod
    def save(cls, filename):
        fullname = os.path.join(cls.filepath, filename)
        wf = wave.open(fullname, 'wb')
        wf.setnchannels(cls.num_write_channel)
        wf.setsampwidth(cls.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(cls.sample_rate)
        wf.writeframes(b''.join(cls.frames))
        wf.close()
        return {
            'name': os.path.basename(filename),
            'dir': os.path.dirname(filename),
            'path': filename,
            'size': len(cls.frames)
        }


class Producer(threading.Thread):
    filename: str

    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.recorder = Recorder()

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener1:
            listener1.join()

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('t'):
            print("on_press called!")
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            self.filename = f'rec-{timestamp}.wav'
            threading.Thread(target=self.recorder.record).start()

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('s'):
            print("on_release called!")
            self.recorder.stopNow()
            file = self.recorder.save(self.filename)
            self.queue.put(file)


class Consumer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.running = True

    def run(self):
        while self.running:
            file_meta = self.queue.get()
            t = S2TConverter(file_meta)
            t.start()
            self.queue.task_done()


if __name__ == '__main__':
    q = queue.Queue()
    producer = Producer(q)
    consumer = Consumer(q)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
    # test
