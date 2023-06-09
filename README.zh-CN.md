# 欢迎

[English README](https://github.com/Smilence7/TalkGPT/blob/main/README.md)

### 介绍
TalkGPT是一个基于一系列开放API服务的语音对话AI助手，计划提供一系列定制化功能。

### 系统结构

TalkGPT的基本结构

![talkgpt_1x](https://user-images.githubusercontent.com/12277570/233575831-0a669fda-a4e9-40b7-a4e8-98ecc437bfa0.png)

### 快速开始

#### 1. 申请API访问密钥  
- 你需要拥有一个OpenAI账户，在用户页面中创建一个api_key，用于语音转文字API访问和聊天完成API访问。
- 你需要拥有一个AWS账户，在凭证管理页面上创建一个IAM帐户，并创建一组IAM帐户的凭据，用于文本转语音API访问。

#### 2. 下载此项目  
```shell
git clone https://github.com/Smilence7/TalkGPT.git
cd ./TalkGPT
```

#### 3. 安装所需库  
- 项目依赖python环境，建议使用python-3.8版本
- 安装第三方库 
```shell
pip3 install -r requirements.txt
```

#### 4. 填写配置文件  
```shell
cp ./config/config.yml.example ./config/config.yml
vim ./config/config.yml
```
将你申请的秘钥填写在对应位置，根据需要修改其他配置

#### 5. 运行  
```shell
python ./src/main.py
```

#### 6. 按住热键说话  
- 按住键盘上的“T”键说话。  
- 释放键后，根据网络状况，约在1~5秒后，你将听到来自输出设备的响应

#### 7. 关闭程序
kill it.

## 功能
你可以像在ChatGPT网站上一样与GPT-3.5进行交谈，但以语音输入和输出的形式。

#### 1. 自由模式
没有输入/输出限制。

#### 2. 润色模式
说几句话，程序将用更好或更自然的版本进行回应，主要用于语言学习。

## 路线图
- [x] 语音到语音的工作流
- [ ] 实现热键绑定和可视化配置的GUI
- [ ] 打包
- [ ] 本地微调的文本转语音(TTS)模型 (参考AI xQc
- [ ] 在GUI中显示文字聊天记录
- [ ] 功能：重放最后一句回答
