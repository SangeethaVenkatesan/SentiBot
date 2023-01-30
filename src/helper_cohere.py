import os 
from dotenv import load_dotenv
from loguru import logger
import cohere
from time import time,sleep
import numpy as np
import json
import cohere 
import re
import pandas as pd
from torch.nn.functional import cosine_similarity
import torch
import warnings

warnings.filterwarnings("ignore")





load_dotenv()


class CohereClient:
    def __init__(self):
        self.co = self.get_cohere_client()
        
        

    
    def get_cohere_client(self):
        COHERE_API_KEY = os.environ.get('COHERE_API_KEY')
        co = cohere.Client(COHERE_API_KEY)
        return co

    def similar_logs(self,utterance,chatroom_id,final_conversations):
        updated_conversation = final_conversations.copy()
        updated_conversation.pop()
        df = pd.DataFrame(updated_conversation, columns=['Text'])
        corpus_embeddings_model = self.co.embed(texts=df['Text'].tolist())
        corpus_embeddings_embed = corpus_embeddings_model.embeddings
        corpus_embeddings_embed = corpus_embeddings_embed / \
            np.linalg.norm(corpus_embeddings_embed, axis=1, keepdims=True)
        query_embedding = self.co.embed([utterance]).embeddings[0]
        # load the dataset(knowledge base)
        result_dict = {}
        '''find the closest `top_k` queries of the corpus for the user query based on cosine similarity'''

        x = torch.tensor(query_embedding)
        y = torch.tensor(corpus_embeddings_embed)
        top_k=5

        # use cosine-similarity and torch.topk to find the highest `top_k` scores
        cos_scores = cosine_similarity(x, y)
        top_results = torch.topk(cos_scores, k=min(top_k, df.shape[0]))
        # filter dataframe by list of index
        df_new = df.iloc[top_results[1], :]
        # add matched score
        df_new['Score'] = ["{:.4f}".format(value) for value in top_results[0]]
        # select top_k responses
        responses = df_new.to_dict('records')
        logger.debug(f'Query Asked: {utterance}')
        logger.debug(f'Similar logs found: \n {responses}')
        return responses





    






        
