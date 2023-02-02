from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, Request
from loguru import logger
import json
import helper_database
import helper_nlp
import helper_cohere
import helper_generation
import uvicorn

app = FastAPI()
logger.debug('Application started.')


#models
class Message(BaseModel):
  value: str
  chatroom_id: str = None
  user_id: str

  def __getitem__(self, item):
    return getattr(self, item)


class UserId(BaseModel):
  user_id: str

  def __getitem__(self, item):
    return getattr(self, item)


class ChatroomId(BaseModel):
  chatroom_id: str
  user_id: str

  def __getitem__(self, item):
    return getattr(self, item)


@app.get("/")
async def health_check():
  # logger.debug("Health check hit")
  return {'statusCode': 200, 'body': json.dumps('Healthy')}


@app.get("/get_chatroom_ids")
async def get_chat_room_ids(userId: UserId, request: Request):
  user_id = userId["user_id"]
  client_db = helper_database.SociBotDB()
  try:
    chatroom_ids = client_db.get_chat_room_ids(user_id)
  except Exception as e:
    return {'statusCode': 500, 'body': str(e)}
  if chatroom_ids is None:
    return {'statusCode': 404, 'body': 'User not found'}
  return {'statusCode': 200, 'body': chatroom_ids}


@app.post("/chat")
def get_response(message: Message, request: Request):
  #### FAST API HANDLER CODE #######
  client_gen_cohere = helper_generation.CohereGeneration()
  body = client_gen_cohere.process_chat_message(message)
  return {'statusCode': 200, 'body': body}


@app.delete("/delete_chatroom")
async def delete_chatroom(chatroom: ChatroomId, request: Request):
  user_id = chatroom["user_id"]
  chatroom_id = chatroom["chatroom_id"]
  client_db = helper_database.SociBotDB()
  try:
    client_db.delete_chat_room_id(user_id, chatroom_id)
    return {"statusCode": 200, "message": "Chatroom deleted successfully"}
  except Exception as e:
    logger.error(f'Error while deleting chatroom: {e}')
    return {'statusCode': 500, 'body': 'Error while deleting chatroom'}


uvicorn.run(app, host="0.0.0.0", port=8080)
