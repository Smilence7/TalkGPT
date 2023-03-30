import logging.config
from os import path
import queue
from components import Producer, Consumer


if __name__ == '__main__':
    cur_dir = path.dirname(path.abspath(__file__))
    log_conf = path.join(path.dirname(cur_dir), 'config/logging.conf')
    logging.config.fileConfig(log_conf)
    save_dir = path.join(path.dirname(cur_dir), 'saved/record/')
    q = queue.Queue()
    producer = Producer(save_dir, q)
    consumer = Consumer(q)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
