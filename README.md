# Welcome

### What is it

TalkGPT is a speech-to-speech AI assistant based on a set of open API services and offers a range of customized features.

### System Structure

Basic structure of TalkGPT


![talkgpt_1x](https://user-images.githubusercontent.com/12277570/233575831-0a669fda-a4e9-40b7-a4e8-98ecc437bfa0.png)


### Quick Start

1. Apply for API access key
- You need an OpenAI account to create an api_key in your user page, which will be used for speech-to-text API access & chat completion API access.
- You need an AWS account to create an IAM account, and create a set of credentials for your IAM account on the credential management page, which will be used for text-to-speech API access.

2. Download the project
```python
git clone git@github.com:Smilence7/TalkGPT.git
cd ./TalkGPT
```

3. Install required libraries  
`pip install -r requirements.txt`

4. Run  
`python ./src/main.py`

5. Push to talk
Press and hold `T` on your keyboard to talk.  
You will hear the response from your output device around 1~5 seconds after releasing the key, depending on your network condition.
