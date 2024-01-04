import dotenv
dotenv.load_dotenv()
import json
import openai
import os
import re
import requests
import time

openai.api_key = openai_api_key = os.environ['OAI_SERVER_API_KEY']
if 'HOMEBREW_PREFIX' in os.environ:
    openai.api_base = openai_api_base = "http://127.0.0.1:8081"
elif 'BITNAMI_APP_NAME' in os.environ:
    openai.api_base = openai_api_base = "http://localhost:10001"
else:
    raise ValueError('Did not detect HOMEBREW_PREFIX (Mac, local) or BITNAMI_APP_NAME (Lightsail, remote) in environment variables.')
# openai.api_base = openai_api_base = "https://www.ericmusa.com"

auth_headers = {
    'Authorization': f'Bearer {openai_api_key}',
    'Content-Type': 'application/json',
}

class ConversationManager:
    
    PRIMER = [
        {'role': 'system', 'content': 'You are an AI Assistant. The user will generally ask trivia questions about any topic and it is your job to answer their question as briefly as possible and to the best of your abilities. If you are not sure of the response or the information is outdated, say so, but also briefly.'},
        {'role': 'user', 'content': 'Hello!'},
        {'role': 'assistant', 'content': 'Hello! How may I help you today?'},
        # {'role': 'system', 'content': 'You are an AI Assistant. The user will generally ask trivia questions about any topic and it is your job to answer their question as briefly as possible and to the best of your abilities. If you are not sure of the response or the information is outdated, say so, but also briefly.'},
        # {'role': 'Human', 'content': 'Hello!'},
        # {'role': 'AI', 'content': 'Hello! How may I help you today?'},
    ]

    FILENAME_TEMPLATE = 'monkeybot-{}-{}.txt'
    FILENAME_TEMPLATE_RE = 'monkeybot-(\\d+)-(\\d+).txt'
    
    def __init__(self, directory='conversations') -> None:
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.directory = directory
        self.messages, self.filename = self.load_conversation()
        self.active_model = self.get_model()['model_name']

    def get_latest_conversation(self):
        latest_filenum = -1
        ts = None
        for fname in os.listdir(self.directory):
            result = re.findall('monkeybot-(\\d+)-(\\d+).txt', fname)
            assert len(result) == 1, f'should only be one match in {fname}'
            index, timestamp = [int(_) for _ in result[0]]
            if index > latest_filenum:
                latest_filenum = index
                ts = timestamp
        return latest_filenum, ts or int(time.time())

    def load_conversation(self):
        latest_filenum, timestamp = self.get_latest_conversation()
        if latest_filenum == -1:
            filename = self.FILENAME_TEMPLATE.format(1, timestamp)
            print(f'No existing conversation files found, creating {filename}')
            with open(os.path.join(self.directory, filename), 'w') as f:
                messages = list(self.PRIMER)
                json.dump(messages, f)
                for message in messages: self.print_message(message)
        else:
            filename = self.FILENAME_TEMPLATE.format(latest_filenum, timestamp)
            print(f'Prior conversation found, {filename}')
            with open(os.path.join(self.directory, filename), 'r') as f:
                messages = json.load(f)
                for message in messages: self.print_message(message)
        return messages, filename

    def reset_conversation(self):
        latest_filenum, timestamp = self.get_latest_conversation()
        if latest_filenum == -1:
            filename = self.FILENAME_TEMPLATE.format(1, timestamp)
            print(f'No existing conversation files found, creating {filename}')
        else:
            filename = self.FILENAME_TEMPLATE.format(latest_filenum+1, int(time.time()))
            print(f'Creating new conversation, {filename}')
        with open(os.path.join(self.directory, filename), 'w') as f:
            json.dump(self.PRIMER, f)
        for message in self.PRIMER: self.print_message(message)
        self.messages = list(self.PRIMER)
        self.filename = filename

    def get_model(self, headers=auth_headers):
        return requests.get(url=f'{openai_api_base}/model', headers=headers).json()

    def complete_chat(self, user_input, max_tokens=64):
        if user_input == 'RESTART':
            time.sleep(0.3)
            print()
            print('RESETTING MESSAGE HISTORY')
            print()
            self.reset_conversation()
            return 'CONVERSATION RESET'
        self.messages.append({'role': 'user', 'content': user_input})
        chat_completion = openai.ChatCompletion.create(model=self.active_model, messages=self.messages, max_tokens=max_tokens)
        ai_response = chat_completion.choices[0].message.content
        trimmed_ai_response = self.trim_incomplete_response(ai_response, comma_is_delimiter=True)
        self.messages.append({'role': 'assistant', 'content': trimmed_ai_response})
        # messages.append({'role': 'AI', 'content': trimmed_ai_response})
        self.print_message(self.messages[-1])
        with open(os.path.join(self.directory, self.filename), 'w') as f:
            json.dump(self.messages, f)
        return trimmed_ai_response

    @staticmethod
    def print_message(message):
        assert isinstance(message, dict) and all(_ in message for _ in ['role', 'content'])
        print(f"{message['role']}: {message['content']}")

    def trim_incomplete_response(self, response, delimiters=('.', '!', '?'), comma_is_delimiter=False):
        if not response.endswith(delimiters):
            i = len(response)
            while i>0:
                i -= 1
                if response[i] in delimiters:
                    return response[:i+1]
                elif response[i] == ',' and comma_is_delimiter:
                    return response[:i] + '...'
        return response


if __name__ == '__main__':

    cm = ConversationManager()
    while True:
        user_input = input('user: ')
        cm.complete_chat(user_input)
