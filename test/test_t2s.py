from src.service import T2SConverter
from os import path
import yaml
from src.service import play, play_bytes

parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
conf = path.join(parent_dir, 'config/client.yml')
with open(conf, 'r') as f:
    config = yaml.safe_load(f)


def test_t2s():
    save_path = path.join(config['save_dir'], "speech.mp3")
    t2s = T2SConverter(config)
    data = t2s.convert_and_get("This is amazon polly client."
                               " Hearing this speech means the test is success!", save_path)
    print(save_path)
    print(data)
    return save_path, data


def test_play():
    file = path.join(config['save_dir'], "speech.wav")
    play(file)


def test_t2s_and_play():
    file, _ = test_t2s()
    play(file)


def test_t2s_and_play_bytes():
    _, data = test_t2s()
    play_bytes(data)


if __name__ == '__main__':
    # test_t2s()
    # test_play()
    test_t2s_and_play()
    # test_t2s_and_play_bytes()
