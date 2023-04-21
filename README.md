# Welcome

[中文README](https://github.com/Smilence7/TalkGPT/blob/main/README.zh-CN.md)

## What is it

TalkGPT is a speech-to-speech AI assistant based on a set of open API services and offers a range of customized features.

## System Structure

Basic structure of TalkGPT


![talkgpt_1x](https://user-images.githubusercontent.com/12277570/233575831-0a669fda-a4e9-40b7-a4e8-98ecc437bfa0.png)


## Quick Start

#### 1. Apply for API access keys
- To use the speech-to-text and chat completion APIs, you'll need an OpenAI account to create an API key in your user page.
- To use the text-to-speech API, you'll need an AWS account to create an IAM account and a set of credentials on the credential management page.

#### 2. Download the project
```shell
git clone https://github.com/Smilence7/TalkGPT.git
cd ./TalkGPT
```

#### 3. Install required libraries  
- Python 3 is required, and the testing was done on version 3.8.
- Install the required third-party libraries.
```shell
pip3 install -r requirements.txt
```

#### 4. Configure your settings
```shell
mv ./config/config.yml.example ./config/config.yml
vim ./config/config.yml
```
Set your Access Keys in the config file and adjust the properties to suit your needs.

#### 5. Run the program
```shell
python3 ./src/main.py
```

#### 6. Speak to it
- Press and hold `T` on your keyboard to talk.  
- You will hear the response from your output device in around 1-5 seconds, depending on your network condition.

#### 7. Stop the program
Just kill it.

## Features
You can have a conversation with the application, just like you would on the ChatGPT website, but in the form of voice input and output.
#### 1. Free mode
No input/output restriction.
#### 2. Polish mode
Speak several sentences and the program will respond with a better or more native version. Primarily intended for language improvement purposes.

## Todo
#### 1. Packaging
#### 2. Implement user interface for key binding & configuration

