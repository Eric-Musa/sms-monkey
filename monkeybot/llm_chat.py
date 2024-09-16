import dotenv
dotenv.load_dotenv()
import openai
from openai.error import APIError
import os
import requests
import time

BUSY_MESSAGE = 'I apologize, I am unable to answer that question at present, could you please repeat yourself in a moment?'

openai.api_key = openai_api_key = os.environ['OAI_SERVER_API_KEY']
if 'HOMEBREW_PREFIX' in os.environ:
    openai.api_base = openai_api_base = "http://127.0.0.1:8081"
# elif 'BITNAMI_APP_NAME' in os.environ:
#     openai.api_base = openai_api_base = "http://localhost:10001"
else:
    openai.api_base = openai_api_base = "http://localhost:10001"
    # raise ValueError('Did not detect HOMEBREW_PREFIX (Mac, local) or BITNAMI_APP_NAME (Lightsail, remote) in environment variables.')
# openai.api_base = openai_api_base = "https://www.ericmusa.com"

auth_headers = {
    'Authorization': f'Bearer {openai_api_key}',
    'Content-Type': 'application/json',
}


# def get_model(headers=auth_headers):
#     model = requests.get(url=f'{openai_api_base}/model', headers=headers).json()  # ['model_name']
#     print('model:', model)
#     return model


def chat(messages, max_tokens, retries=3, timeout=2):
    for _ in range(retries):
        try:
            # chat_completion = openai.ChatCompletion.create(model=get_model(), messages=messages, max_tokens=max_tokens)
            chat_completion = openai.ChatCompletion.create(model='local-llm', messages=messages, max_tokens=max_tokens)
            return chat_completion.choices[0].message.content
        except APIError as e:
            print(e)
            time.sleep(timeout)
    print(f'Max attempts ({retries}) hit, returning BUSY_MESSAGE')
    return BUSY_MESSAGE