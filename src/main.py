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
        self.frames = []
        self.running = True
        self.filepath = '../saved/record'
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.num_read_channel = 1
        self.num_write_channel = 1
        self.stream = None

    def record(self):
        # todo: use logging instead
        print("Start recording...")
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

    def stop_gracefully(self):
        self.running = False

    def stop_now(self):
        if self.stream is not None:
            self.running = False
            time.sleep(1)
            self.stream.stop_stream()
            self.stream.close()
        else:
            # todo: use logging instead
            print("Input stream is null.")

    def save(self, filename):
        if filename is not None:
            if not os.path.exists(self.filepath):
                os.makedirs(self.filepath, 0o755)
            fullname = os.path.join(self.filepath, filename)
            wf = wave.open(fullname, 'wb')
            wf.setnchannels(self.num_write_channel)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            return {
                'name': os.path.basename(filename),
                'dir': os.path.dirname(filename),
                'path': filename,
                'size': len(self.frames)
            }
        else:
            # todo: use logging instead
            print("Filename is null.")


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
            print("on_press called!")
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            self.filename = f'rec-{timestamp}.wav'
            threading.Thread(target=self.recorder.record).start()

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('t') and self.pressing:
            self.pressing = False
            print("on_release called!")
            self.recorder.stop_now()
            file = self.recorder.save(self.filename)
            if file is not None:
                self.queue.put(file)
            else:
                print("Error in saving wav file.")

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


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
