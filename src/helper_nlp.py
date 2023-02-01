import os 
from dotenv import load_dotenv
from loguru import logger
import openai
from time import time,sleep
import numpy as np
import json
import cohere 
import re

load_dotenv()



class NLPClient:
    def __init__(self):
        self.get_nlp_client()

    
    def get_nlp_client(self):
        openai.api_key = os.environ.get('OPEN_API_KEY')
    
    
    def open_file(self,filepath):
        with open(filepath,'r',encoding='utf-8') as infile:
            return infile.read()
    
    def gpt3_completion(self,prompt, engine='text-davinci-003',temp=1.1,top_p=1.0,tokens=2000,freq_pen=0.0,pres_pen=0.0,stop=['USER:']):
        max_retry = 5
        retry = 0
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        while True:
            try:
                response = openai.Completion.create(
                    engine = engine,
                    prompt = prompt,
                    temperature=temp,
                    max_tokens = tokens,
                    top_p = top_p,
                    frequency_penalty = freq_pen,
                    presence_penalty = pres_pen,
                    stop = stop)
                text = response['choices'][0]['text'].strip()
                text = re.sub('\s+',' ',text)
                return text 

            except Exception as oops:
                retry += 1
                if retry >= max_retry:
                    return 'GPT3 error: %s' % oops
                print('Error communicating with OpenAI:',oops)
                exit()
                sleep(1)

    
    def get_completion(self,block):
        file_path = os.path.join(os.path.dirname(__file__), 'prompts', 'prompt_senti.txt')
        prompt = self.open_file(file_path).replace('<<CONVERSATION>>',block)
        logger.debug(f'The final prompt! \n {prompt}')
        response = self.gpt3_completion(prompt)
        logger.debug(f'The final response from bot: {response}')
        return response
