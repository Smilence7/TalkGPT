from src.service import T2SConverter
from os import path
import yaml
import src.component as component

parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
conf = path.join(parent_dir, 'config/client.yml')
with open(conf, 'r') as f:
    config = yaml.safe_load(f)


def test_tts():
    save_path = path.join(config['save_dir'], "speech.mp3")
    tts = T2SConverter(config, save_path)
    data = tts.convert_and_get("This is amazon polly client."
                               " Hearing this speech means the test is success!")
    print(save_path)
    print(data)
    return save_path, data


def test_play():
    file = path.join(config['save_dir'], "speech.wav")
    component.play(file)


def test_tts_and_play():
    file, _ = test_tts()
    component.play(file)


def test_tts_and_play_bytes():
    _, data = test_tts()
    component.play_bytes(data)


if __name__ == '__main__':
    # test_tts()
    # test_play()
    test_tts_and_play()
    # test_tts_and_play_bytes()
