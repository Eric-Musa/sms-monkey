import hashlib
import json
import os
import re
import time
from llm_chat import chat, BUSY_MESSAGE

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
    
    
    def __init__(self, convo_directory='conversations', verbose=True) -> None:
        if not os.path.isdir(convo_directory):
            os.mkdir(convo_directory)
        self.convo_directory = convo_directory
        self.verbose = verbose
    
    @staticmethod
    def hash_number(user_number):
            # Choose a hash function. Here we use SHA256.
        hash_object = hashlib.sha256()
        
        # Update the hash object with the user ID.
        # The user ID should be encoded to bytes.
        hash_object.update(user_number.encode())
        
        # Return the hexadecimal digest of the user ID.
        return hash_object.hexdigest()
        # return str(hash(str(user_number)))

    def get_latest_conversation(self, conversation_directory):
        latest_filenum = -1
        ts = None
        if not os.path.isdir(conversation_directory):
            print(f'Created conversation directory: {conversation_directory}', flush=True)
            os.mkdir(conversation_directory)
        for fname in os.listdir(conversation_directory):
            result = re.findall('monkeybot-(\\d+)-(\\d+).txt', fname)
            if result:
                assert len(result) == 1, f'should only be one match in {fname}'
                index, timestamp, = [int(_) for _ in result[0]]
                if index > latest_filenum:
                    latest_filenum = index
                    ts = timestamp
        return latest_filenum, ts or int(time.time())

    def load_conversation(self, conversation_directory):
        latest_filenum, timestamp = self.get_latest_conversation(conversation_directory)
        if latest_filenum == -1:
            filename = self.FILENAME_TEMPLATE.format(1, timestamp)
            print(f'No existing conversation files found, creating {filename}')
            with open(os.path.join(conversation_directory, filename), 'w') as f:
                messages = list(self.PRIMER)
                json.dump(messages, f)
                for message in messages: self.print_message(message)
        else:
            filename = self.FILENAME_TEMPLATE.format(latest_filenum, timestamp)
            print(f'Prior conversation found, {filename}')
            with open(os.path.join(conversation_directory, filename), 'r') as f:
                messages = json.load(f)
                for message in messages: self.print_message(message)
        return messages, filename

    def reset_conversation(self, conversation_directory):
        latest_filenum, timestamp = self.get_latest_conversation(conversation_directory)
        if latest_filenum == -1:
            filename = self.FILENAME_TEMPLATE.format(1, timestamp)
            print(f'No existing conversation files found, creating {filename}')
        else:
            filename = self.FILENAME_TEMPLATE.format(latest_filenum+1, int(time.time()))
            print(f'Creating new conversation, {filename}')
        with open(os.path.join(conversation_directory, filename), 'w') as f:
            json.dump(self.PRIMER, f)
        for message in self.PRIMER: self.print_message(message)
        # self.messages = list(self.PRIMER)
        # self.filename = filename


    def complete_chat(self, user_input, user_number, max_tokens=64):
        number_hash = self.hash_number(user_number)
        conversation_directory = os.path.join(self.convo_directory, number_hash)
        if user_input == 'RESTART':
            time.sleep(0.3)
            print()
            print('RESETTING MESSAGE HISTORY')
            print()
            self.reset_conversation(conversation_directory)
            return f'Conversation Reset... {self.PRIMER[-1]["content"]}', len(self.PRIMER)
        
        messages, filename = self.load_conversation(conversation_directory)
        
        ai_response = chat(messages, max_tokens)
        if ai_response == BUSY_MESSAGE:
            return BUSY_MESSAGE, len(messages)

        trimmed_ai_response = self.trim_incomplete_response(ai_response, comma_is_delimiter=True)
        
        messages.append({'role': 'user', 'content': user_input})
        messages.append({'role': 'assistant', 'content': trimmed_ai_response})
        # messages.append({'role': 'AI', 'content': trimmed_ai_response})
        self.print_message(messages[-1])
        with open(os.path.join(conversation_directory, filename), 'w') as f:
            json.dump(messages, f)
        return trimmed_ai_response, len(messages)

    def print_message(self, message):
        assert isinstance(message, dict) and all(_ in message for _ in ['role', 'content'])
        if self.verbose: print(f"{message['role']}: {message['content']}")

    @staticmethod
    def trim_incomplete_response(response, delimiters=('.', '!', '?'), comma_is_delimiter=False):
        if not response.endswith(delimiters):
            i = len(response)
            while i > 0:
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
