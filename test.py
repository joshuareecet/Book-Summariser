#Imports required for gemini access
from google import genai
from google.genai import types
from time import sleep #to limit the no. of requests per minute on free api
from llama_cpp import Llama

#Imports from project
import initial_setup
from core_classes import Book
from user_interaction import get_file_path, get_int

#Importing constants + module variables
from initial_setup import (combine_summary, part_summary, 
                           query_fiction, query_non_fiction, local_model,
                           shelf, use_local_model, context_window_limit, gpu_layers)


llm = Llama(
        model_path = local_model._raw_path,
        n_gpu_layers = -1, 
        # seed=1337, # Uncomment to set a specific seed
        n_ctx = int(context_window_limit / 10) # .env file this
        )

#generating response
response = llm(
    'Q: What is the size of the moon. A: ', # Prompt
    max_tokens = None, # Generate up to 32 tokens, set to None to generate up to the end of the context window
    stop = ['Q: '], 
    echo = False #
) # Generate a completion, can also call create_completion
print(response)