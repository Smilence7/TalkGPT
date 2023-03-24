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
    def __init__(self, p, dir_path, chunk_size=1024, sample_rate=44100):
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
        # todo: use logging instead
        print("Start recording...")

        self.open_stream()
        while self.running:
            try:
                data = self.stream.read(self.chunk_size)
                self.frames.append(data)
            except IOError:
                print("IOError")
        self.close_stream()

    def stop_gracefully(self):
        self.running = False

    def stop_now(self):
        print("Stop recording...")
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
            # todo: use logging instead
            print("Error occurred when saving, frames content is empty.")
            return
        if filename is None:
            # todo: use logging instead
            print("Error occurred when saving, filename is null.")
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
    def __init__(self, dir_path, queue):
        super().__init__()
        self.dir_path = dir_path
        self.queue = queue
        self.p = pyaudio.PyAudio()
        self.recorder = None
        self.pressing = False
        self.filename = None
        self.recorder_threads = []
        self.idx = -1

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('t') and not self.pressing:
            self.pressing = True
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            self.filename = f'rec-{timestamp}.wav'
            self.recorder = Recorder(self.p, self.dir_path)
            self.recorder_threads.append(threading.Thread(target=self.recorder.record))
            self.idx += 1
            self.recorder_threads[self.idx].start()
            print(self.recorder_threads[self.idx].getName(), "started")

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('t') and self.pressing:
            self.pressing = False
            # self.recorder.stop_now()
            self.recorder.stop_gracefully()
            self.recorder_threads[self.idx].join()
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
    save_dir = os.environ['HOME'] + '/s2s_saved/record'
    q = queue.Queue()
    producer = Producer(save_dir, q)
    consumer = Consumer(q)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
