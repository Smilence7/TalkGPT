import logging.config
from os import path
import queue
import openai
import yaml

from component import Producer, Consumer


class S2SApp:
    def __init__(self):
        cur_dir = path.dirname(path.abspath(__file__))
        log_conf = path.join(path.dirname(cur_dir), 'config/logging.conf')
        logging.config.fileConfig(log_conf)
        # save_dir = path.join(path.dirname(cur_dir), 'saved/record/')
        conf = path.join(path.dirname(cur_dir), 'config/client.yml')
        with open(conf, 'r') as f:
            self.config = yaml.safe_load(f)
        q = queue.Queue()
        openai.api_key = self.config['api_key']['openai']
        self.producer = Producer(self.config['save_dir'], q)
        self.consumer = Consumer(q)

    def activate(self):
        self.producer.start()
        self.consumer.start()
        self.producer.join()
        self.consumer.join()


if __name__ == '__main__':
    app = S2SApp()
    app.activate()
