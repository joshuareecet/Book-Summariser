from dotenv import load_dotenv
import os
from pathlib import Path
import json
from core_classes import Bookshelf

#Constants
root_dir = fake = Path(__file__).parent
environment_file_path = Path(".env")
prompts_dir = root_dir / 'Prompts'

shelf = Bookshelf()

#Creating subdirectories
ebook_dir_name = root_dir / 'ebooks'
if ebook_dir_name.is_dir() == False:
    print("ebook directory missing, creating directory...")
    ebook_dir_name.mkdir()

local_llm_dir = root_dir / 'llm_models'
if local_llm_dir.is_dir() == False:
    print("Local LLM directory missing, creating directory...")
    local_llm_dir.mkdir()
    print("Local LLM directory created, please put your chosen .gguf model inside llm_models.\n"
    "You can find recommended models in Readme.md or on the github repo")

if prompts_dir.is_dir() == False:
    print("Prompts directory missing, creating directory...")
    prompts_dir.mkdir()
    print("Prompts directory created, please put download the prompt files from github or create your own.")

#Getting API key and setting as environment variable

def fill_environment_file():
    api_key = input("Please enter your gemini API key: ")
    
    context_window_limit = 130000 #Default
    print("Please edit the environment file context window limit if you have downloaded a custom model.")
    
    use_local_model = input("Would you like to use local text generation? Please enter True or False. ")
    use_local_model = use_local_model.lower() == 'true'
    
    gpu_layers = input("Would you like to enable GPU acceleration for local text generation?\n" \
    "Please enter True or False")
    gpu_layers = -1 if gpu_layers.lower() == 'true' else 0

    with open(".env", "w") as environment:
        environment.write(f"GEMINI_API_KEY = \"{api_key}\"\n")
        environment.write(f"USE_GPU = {gpu_layers}\n")
        environment.write(f"USE_LOCAL_MODEL = {use_local_model}\n")
        environment.write(f"CONTEXT_WINDOW = {context_window_limit}\n")
    
    #Now loading as environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") # this is not used
    context_window_limit = int(os.getenv("CONTEXT_WINDOW"))
    use_local_model = os.getenv("USE_LOCAL_MODEL", False).lower() == 'true'
    gpu_layers = -1 if os.getenv("USE_GPU", False).lower() == 'true' else 0

if environment_file_path.exists():
    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY") # this is not used
        context_window_limit = int(os.getenv("CONTEXT_WINDOW"))
        use_local_model = os.getenv("USE_LOCAL_MODEL", False).lower() == 'true'
        gpu_layers = -1 if os.getenv("USE_GPU", False).lower() == 'true' else 0
    except:
        print("There was an error loading the environment file, please enter Y/N if you would like to reset it: ")
        fill = input()
        if fill.lower() == 'y':
            fill_environment_file()
        else:
            raise ValueError("Please manually fill your environment file. Stopping application now.")
else:
    try:
        fill_environment_file()
    except:
        raise FileNotFoundError("There was an error writing the API_Keys, please restart or manually create the environment file")


#Loading LLM model

LLM_paths = [f for f in local_llm_dir.iterdir() if f.is_file()]

if LLM_paths == []:
    print("No local LLM files detected. \n" \
    "Defaulting to Gemini API mode.\n" \
    "You can find recommended models in Readme.md or on the github repo.")
    #Add something to switch to gemini API
    local_model = None
elif len(LLM_paths) == 1:
    local_model = LLM_paths[0]
else:
    i = 0
    print("Please select your LLM model: ")
    for items in os.scandir(local_llm_dir):
        print(f"{i}: {items.name}")
        i += 1
    local_model = LLM_paths[i]
    print(local_model)
    local_model = Path(local_model)
    #Should add some kind of memory so you don't need to pick everytime.

#Loading prompts - maybe we should implement just in time loading?

# def load_prompt(prompt_version):
#     try:
#         if prompt_version == 'fiction_chapter':
#             with open(prompts_dir / "query_fiction.txt") as file:
#                 query_fiction = file.read()
#         elif prompt_version == 'non_fiction_chapter':
#             with open(prompts_dir / "query_non_fiction.txt") as file:
#                 query_non_fiction = file.read()
#         elif prompt_version == 'combine_summary':
#             with open(prompts_dir / "combine_part_summary.txt") as file:
#                 combine_summary = file.read()
#         elif prompt_version == 'book_part_summary':
#             with open(prompts_dir / "book_part_summary.txt") as file:
#                 part_summary = file.read()
#     except FileNotFoundError:
#         raise FileNotFoundError(f"ERROR: could not load {prompt_version}")

try:
    with open(prompts_dir / "query_fiction.txt") as file:
        query_fiction = file.read()

    with open(prompts_dir / "query_non_fiction.txt") as file:
        query_non_fiction = file.read()

    with open(prompts_dir / "combine_part_summary.txt") as file:
        combine_summary = file.read()

    with open(prompts_dir / "book_part_summary.txt") as file:
        part_summary = file.read()
        
except FileNotFoundError:
    raise FileNotFoundError("ERROR: could not find one of query_fiction.txt or query_non_fiction.txt.")