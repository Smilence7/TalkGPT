import logging
import platform
import os.path
import queue
import threading
import time
import wave
from converter import S2TConverter

import pyaudio
from pynput import keyboard


class Recorder:
    def __init__(self, chunk_size=1024, sample_rate=44100):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.running = True
        self.filepath = os.environ['HOME'] + '/s2s_saved/record'
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.num_read_channel = 1
        self.num_write_channel = 1
        self.lock = threading.Lock()

    def record(self):
        # todo: use logging instead
        print("Start recording...")

        self.open_stream()
        while self.running:
            print("test: loop")
            data = self.stream.read(self.chunk_size)
            self.frames.append(data)
        self.close_stream()

    def stop_gracefully(self):
        self.running = False

    def stop_now(self):
        print("Stop recording...")
        self.close_stream()

    def open_stream(self):
        print("test: open waiting for lock",)
        with self.lock:
            print("test: open in lock")
            self.running = True
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=self.num_read_channel,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)
        print("test: open out lock")

    def close_stream(self):
        print("test: close waiting for lock")
        if self.running:
            with self.lock:
                print("test: close in lock")
                self.running = False
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
        print("test: close out lock")

    def save(self, filename):
        if not self.frames:
            # todo: use logging instead
            print("Error occurred when saving, frames content is empty.")
            return
        if filename is None:
            # todo: use logging instead
            print("Error occurred when saving, filename is null.")
            return
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath, 0o755)
        fullname = os.path.join(self.filepath, filename)
        wf = wave.open(fullname, 'wb')
        wf.setnchannels(self.num_write_channel)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.frames = []
        return {
            'name': os.path.basename(filename),
            'dir': os.path.dirname(filename),
            'path': filename,
            'size': len(self.frames)
        }


class Producer(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.recorder = Recorder()
        self.pressing = False
        self.filename = None

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('t') and not self.pressing:
            self.pressing = True
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            self.filename = f'rec-{timestamp}.wav'
            t = threading.Thread(target=self.recorder.record)
            t.start()
            print(t.getName(), "started")

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('t') and self.pressing:
            self.pressing = False
            self.recorder.stop_now()
            file = self.recorder.save(self.filename)
            if file is not None:
                self.queue.put(file)

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            print("Start listening...")
            listener.join()
        print("End listening...")


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
