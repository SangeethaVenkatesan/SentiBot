import cohere
import helper_cohere
from loguru import logger


import warnings

warnings.filterwarnings("ignore")


class CohereGeneration:
    def __init__(self):
        self.model = 'command-xlarge-nightly'
        self.max_tokens = 2000
        self.temperature = 0.9
        self.k = 0
        self.p = 0.7 
        self.frequency_penalty = 0.04,
        self.presence_penalty = 0,
        self.stop_sequences = ["USER:"],
        self.return_likelihoods = 'NONE',
        self.num_generations = 1
        self.co = helper_cohere.CohereClient().co
    
    def open_file(self,filepath):
        with open(filepath,'r',encoding='utf-8') as infile:
            return infile.read()
    

    def cohere_completion(self,block):
        logger.debug(f'Cohere client: {self.co}')
        max_retry = 5
        retry = 0
        prompt = self.open_file('../prompt_senti.txt').replace('<<CONVERSATION>>',block)
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
                    num_generations=self.num_generations)
                logger.debug(f'The response from cohere is \n: {response}')
                text = response.generations[0].text.strip()
                text = re.sub('\s+',' ',text)
                return text 

            except Exception as oops:
                retry += 1
                if retry >= max_retry:
                    return 'Cohere error: %s' % oops
                print('Error communicating with Cohere:',oops)
                exit()
                sleep(1)

         
        




