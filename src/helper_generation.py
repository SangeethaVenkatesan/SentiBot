import cohere
import helper_cohere
from loguru import logger
import helper_database
import helper_nlp
import helper_cohere
import uuid
import re
from time import time,sleep
import os

import warnings

warnings.filterwarnings("ignore")


class CohereGeneration:
    def __init__(self):
        self.model = 'command-xlarge-nightly'
        self.max_tokens = 500
        self.temperature = 0.9
        self.k = 0
        self.p = 0.7 
        self.frequency_penalty = 0.04
        self.presence_penalty = 0.0
        self.stop_sequences = ["USER:"]
        self.return_likelihoods = 'NONE'
        self.num_generations = 1
        self.co = helper_cohere.CohereClient().co
    
    def open_file(self,filepath):
        with open(filepath,'r',encoding='utf-8') as infile:
            return infile.read()
    

    def cohere_completion(self,block):
        logger.debug(f'Cohere client: {self.co}')
        max_retry = 5
        retry = 0
        file_path = os.path.join(os.path.dirname(__file__), 'prompts', 'prompt_senti.txt')
        prompt = self.open_file(file_path).replace('<<CONVERSATION>>',block)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        logger.debug(f'Incoming prompt for cohere: {prompt}')
        while True:
            try:
                response = self.co.generate(
                    model=self.model,
                    prompt= prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    k=self.k,
                    p=self.p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop_sequences=self.stop_sequences,
                    return_likelihoods=self.return_likelihoods,
                    num_generations=self.num_generations
                )
                logger.debug(f'The response from cohere is \n: {response}')
                text = response.generations[0].text.strip()
                text = re.sub('\s+',' ',text)
                logger.debug(f'The reply message from cohere is: {text}')
                return text 

            except Exception as oops:
                retry += 1
                if retry >= max_retry:
                    return 'Cohere error: %s' % oops
                print('Error communicating with Cohere:',oops)
                exit()
                sleep(1)

         
        





    def process_chat_message(self,message):
      utterance = f'USER: {message["value"]}'
      chatroom_id = message['chatroom_id']
      user_id = message['user_id']
      client_db = helper_database.SociBotDB()
      # client_nlp = helper_nlp.NLPClient()
      client_cohere = helper_cohere.CohereClient()
      similar_context = list()
      if not chatroom_id:
        logger.debug(
          'create a chatroom id and map the new user or existing user to chatroom IDs'
        )
        id = f'{uuid.uuid4()}'
        logger.debug(f'chatRoom ID created: {id}')
        client_db.insert_session_users(user_id, id)
        client_db.insert_chat_room_conversations(id, utterance, user_id)
        final_conversations = client_db.get_chat_room_conversations(id)
        logger.debug(f'Final conversations till now: {final_conversations}')
        block = '\n\n'.join(final_conversations) + '\n'
        # response = client_nlp.get_completion(
        #   block)  # This is to test OPENAI completion
        response = self.cohere_completion(block)
        client_db.update_response_chatroom(response, id)
        body = {'utterance': utterance, 'reply': response, 'chatroom_id': id}
    
      else:
        logger.debug('Chatting on the same conversationID')
        client_db.insert_chat_room_conversations(chatroom_id, utterance, user_id)
        final_conversations = client_db.get_chat_room_conversations(chatroom_id)
        logger.debug(f'Final conversations till now: {final_conversations}')
        similar = client_cohere.similar_logs(utterance, chatroom_id,
                                             final_conversations)
        similar_context = [i['Text'] for i in similar] if similar else []
        block = '\n\n'.join(similar_context)
        block += '\n\n'.join(final_conversations) + '\n'
        # response = client_nlp.get_completion(block)
        response = self.cohere_completion(block)
        client_db.update_response_chatroom(response, chatroom_id)
        body = {
          'utterance': utterance,
          'reply': response,
          'chatroom_id': chatroom_id
        }
      return body