from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, Request
from loguru import logger
import json
import uuid
import helper_database
import helper_nlp
import helper_cohere
import helper_generation





app = FastAPI()
logger.debug('Application started.')



class Message(BaseModel):
    value: str
    chatroom_id: str = None
    user_id: str
    def __getitem__(self,item):
        return getattr(self,item)



@app.get("/")
async def health_check():
    # logger.debug("Health check hit")
    return {'statusCode': 200,
            'body': json.dumps('Healthy')}




@app.post("/chat")
def get_response(message:Message, request:Request):
    #### FAST API HANDLER CODE #######
    utterance = f'USER: {message["value"]}'
    chatroom_id = message['chatroom_id']
    user_id = message['user_id']
    client_db = helper_database.SociBotDB()
    client_nlp = helper_nlp.NLPClient()
    client_cohere = helper_cohere.CohereClient()
    client_gen_cohere = helper_generation.CohereGeneration()
    similar_context = list()
    if not chatroom_id:
        logger.debug('create a chatroom id and map the new user or existing user to chatroom IDs')
        id = f'{uuid.uuid4()}'
        logger.debug(f'chatRoom ID created: {id}')
        client_db.insert_session_users(user_id,id)
        client_db.insert_chat_room_conversations(id,utterance,user_id)
        final_conversations = client_db.get_chat_room_conversations(id)
        logger.debug(f'Final conversations till now: {final_conversations}')
        block = '\n\n'.join(final_conversations) + '\n'
        response = client_nlp.get_completion(block) # This is to test OPENAI completion
        # response = client_gen_cohere.cohere_completion(block)
        client_db.update_response_chatroom(response,id)
        body = {'utterance': utterance,'reply':response,'chatroom_id':id}

    else:
        logger.debug('Chatting on the same conversationID')
        client_db.insert_chat_room_conversations(chatroom_id,utterance,user_id)
        final_conversations = client_db.get_chat_room_conversations(chatroom_id)
        logger.debug(f'Final conversations till now: {final_conversations}')
        similar = client_cohere.similar_logs(utterance,chatroom_id,final_conversations)
        similar_context = [i['Text'] for i in similar] if similar else []
        block = '\n\n'.join(similar_context)
        block += '\n\n'.join(final_conversations) + '\n'
        response = client_nlp.get_completion(block)
        # response = client_gen_cohere.cohere_completion(block)
        client_db.update_response_chatroom(response,chatroom_id)
        body = {'utterance': utterance,'reply':response,'chatroom_id':chatroom_id}
    return {
        'statusCode': 200,
        'body': json.dumps(body)
        }
