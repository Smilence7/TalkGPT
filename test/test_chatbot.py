from src.service import ContextGenerator, ChatService
from os import path
import yaml
import openai

parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
conf = path.join(parent_dir, 'config/client.yml')
with open(conf, 'r') as f:
    config = yaml.safe_load(f)

if openai.api_key is None:
    openai.api_key = config['api_key']['openai']


def test_generate_and_chat():
    resp = chatbot.chat(generator.generate("Hello, can you tell a joke?"))
    print("TalkGPT: {0}".format(resp))
    generator.update_response(resp)
    resp = chatbot.chat(generator.generate("Tell another."))
    print("TalkGPT: {0}".format(resp))


if __name__ == '__main__':
    generator = ContextGenerator(config['gpt']['mode'])
    chatbot = ChatService(model=config['gpt']['model'])
    test_generate_and_chat()

