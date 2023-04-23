import logging.config
import threading
from os import path
import queue
import yaml
import sys
from PySide2.QtWidgets import QApplication
from component import Producer, Consumer
from ui import TalkGPTGui


class TalkGPTApp(threading.Thread):
    def __init__(self):
        super().__init__()
        parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
        log_conf = path.join(parent_dir, 'config/logging.conf')
        logging.config.fileConfig(log_conf)
        conf = path.join(parent_dir, 'config/client.yml')
        with open(conf, 'r') as f:
            self.config = yaml.safe_load(f)
        self.q = queue.Queue()
        self.producer = Producer(self.config, self.q)
        self.consumer = Consumer(self.config, self.q)

    def activate(self):
        self.producer.start()
        self.consumer.start()
        self.producer.join()
        self.consumer.join()

    def run(self):
        self.activate()


if __name__ == '__main__':
    app = TalkGPTApp()
    app.start()
    qt_app = QApplication(sys.argv)
    s2s_gui = TalkGPTGui(app)
    s2s_gui.show()
    sys.exit(qt_app.exec_())
