import os
from dotenv import load_dotenv
from loguru import logger
import pymongo
from pymongo import MongoClient
import datetime

load_dotenv()

db_password = os.environ['DB_PASSWORD']
# db_password = os.environ['TESTDB_PASSWORD']

class SociBotDB:
# Client connection setup methods
  def __init__(self):
    self.dbClient = self.get_db_client()
    logger.debug(f'{self.dbClient}')
    self.user_collection = self.get_user_collection()
    self.chat_room_collection = self.get_chat_room_collection()
# Get client
  # create client with mongodb
  def get_db_client(self):
    client = MongoClient(
      f"mongodb+srv://socibot:{db_password}@cluster0.mzer5.mongodb.net/?retryWrites=true&w=majority"
    )
    # client = MongoClient(
    #   f"mongodb+srv://SentiTestBot:{db_password}@cluster0.hyswuko.mongodb.net/?retryWrites=true&w=majority"
    # )

    db = client['socibot']
    # db = client['SentiTestBot']
    return db
    logger.debug(db)
  # get user collection from mongodb
  # get user collection from mongodb
  def get_user_collection(self):
    collection = self.dbClient['users']
    return collection

  # get chatroom collection from mongodb
  def get_chat_room_collection(self):
    collection = self.dbClient['chatrooms']
    return collection

  # get all conversations with chatroom id
  def get_chat_room_conversations(self, chatroom_id):
    result = self.chat_room_collection.find_one({"_id": chatroom_id})
    logger.debug(f'Existing conversations in chatroom: {chatroom_id}')
    conversations = result['conversations']
    final_conversations = [i['message'] for i in conversations]
    return final_conversations

  # get all chatrooms with user id
  def get_chat_room_ids(self, user_id):
    result = self.user_collection.find_one({"_id": user_id})
    logger.debug(f'Existing chatrooms of user: {user_id}')
    chatroom_ids = result['chatroom_ids']
    logger.debug(f'List of chatroom ids: {chatroom_ids}')
    return chatroom_ids

  # delete chatroom from collection
  def delete_chat_room_id(self, user_id, chatroom_id):
    logger.debug(f'Updating chatrooms of user: {user_id}')
    self.user_collection.update_one({"_id": user_id}, {"$pull": {"chatroom_ids": chatroom_id}})
    logger.debug(f'Deleting {chatroom_id} in chatrooms collection.')
    self.chat_room_collection.delete_one({"_id": chatroom_id})
    logger.debug('Chatroom deleted!')

  # update conversation with chatbot input
  def update_response_chatroom(self, response, chatroom_id):
    result = self.chat_room_collection.find_one({"_id": chatroom_id})
    conversations = result['conversations']
    conversations.append({
      "user": "bot",
      "timestamp": datetime.datetime.utcnow().isoformat(),
      "message": response
    })
    result['conversations'] = conversations
    self.chat_room_collection.update_one({"_id": chatroom_id},
                                         {"$set": result},
                                         upsert=True)
    
    logger.debug('chatrooms collection updated!')

  # update conversation with user input
  # update conversation with user input
  def insert_chat_room_conversations(self, chatroom_id, message, user_id):
    # check and insert chatroom id conversations
    result = self.chat_room_collection.find_one({"_id": chatroom_id})
    if not result:
      conversation_data = {
        "_id":
        chatroom_id,
        "conversations": [{
          "user": user_id,
          "timestamp": datetime.datetime.utcnow().isoformat(),
          "message": "USER: Hey SentiBot"
        }, {
          "user":
          "bot",
          "timestamp":
          datetime.datetime.utcnow().isoformat(),
          "message":
          "SentiBot: Hey there! How can I help you today?"
        }, {
          "user": user_id,
          "timestamp": datetime.datetime.utcnow().isoformat(),
          "message": message
        }]
      }
      self.chat_room_collection.update_one({"_id": chatroom_id},
                                           {"$set": conversation_data},
                                           upsert=True)
      logger.debug('chatrooms collection updated!')
    else:
      result = self.chat_room_collection.find_one({"_id": chatroom_id})
      conversations = result['conversations']
      conversations.append({
        "user": user_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "message": message
      })
      result['conversations'] = conversations
      self.chat_room_collection.update_one({"_id": chatroom_id},
                                           {"$set": result},
                                           upsert=True)
      logger.debug('chatrooms collection updated!')

  # user update or creation
  def insert_session_users(self, user_id, chatroom_id):
    # Check if the user ID is present in the collection
    logger.debug(f'{user_id}!')
    result = self.user_collection.find_one({"_id": user_id})
    if result:
      logger.debug(f'user id is present!')
      self.user_collection.update_one({"_id": user_id},
                                      {"$push": {
                                        "chatroom_ids": chatroom_id
                                      }})
    else:
      # User data with an array of session IDs
      user_data = {"_id": user_id, "chatroom_ids": [chatroom_id]}
      # Insert or update the user data with the session IDs
      self.user_collection.update_one({"_id": user_id}, {"$set": user_data},
                                      upsert=True)
      logger.debug(
        f'User ID is not present in USERS collection, hence inserted the chatroom Info!'
      )
