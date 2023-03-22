import os.path
import queue
import threading
import time
import wave

import pyaudio
from pyaudio import Stream
from pynput import keyboard


class Recorder:
    stream: Stream

    def __init__(self, chunk_size=1024, sample_rate=44100):
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.running = True
        self.filepath = './saved/record'
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.num_read_channel = 1
        self.num_write_channel = 1

    def record(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.num_read_channel,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)
        while self.running:
            data = self.stream.read(1024)
            self.frames.append(data)
        self.stream.stop_stream()
        self.stream.close()

    def stopGracefully(self):
        self.running = False

    def stopNow(self):
        self.running = False
        time.sleep(3)
        self.stream.stop_stream()
        self.stream.close()

    def save(self, filename):
        fullname = os.path.join(self.filepath, filename)
        wf = wave.open(fullname, 'wb')
        wf.setnchannels(self.num_write_channel)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return {
            'name': os.path.basename(filename),
            'size': len(self.frames),
            'path': os.path.dirname(filename),
        }


class Producer(threading.Thread):
    filename: str

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.recorder = Recorder()

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('t'):
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            self.filename = f'rec-{timestamp}.wav'
            self.recorder.record()

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('t'):
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
            file = self.queue.get()
            t = threading.Thread(target=self.do_op, args=(file,))
            t.start()

    def do_op(self, file):
        print(file['name'])
        self.queue.task_done()


if __name__ == '__main__':
    q = queue.Queue()
    producer = Producer(q)
    consumer = Consumer(q)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
