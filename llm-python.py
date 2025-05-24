
import os
import sys
import json
import ollama
from ollama import Client
from ollama import chat
from ollama import ChatResponse
from datetime import datetime

_in_memory_responses = []


def check_quit(variable):
    if variable.lower() == "exit":
            sys.exit(0)


def mode_menu():
    user_mode = ""
    options = ["1", "2"]
    while user_mode not in options:
        print("\nWhich mode would you like to use? [enter number]")
        print("1. Send prompt to all models")
        print("2. Send prompt to one chosen model")

        user_mode = input(">> ")

        check_quit(user_mode)
        if user_mode not in options:
            print("Please type the number of your choice (1 or 2)")
    
    return user_mode


def print_models(models_list):
    if not models_list:
        print("No models found. You should not be here")
        return
    else:
        print("\n---Available Models---")
        for model_name in models_list:
            print(f"- {model_name}")


def get_model(models_list):
    user_model = ""
    while user_model not in models_list:
        print("\nEnter the name of the model to use")
        user_model = input(">> ").strip()

        check_quit(user_model)
        if user_model not in models_list:
            print(f"The model {user_model} wasn't a model")

    return user_model


def get_prompt():
    user_prompt = ""
    while user_prompt == "":
        print("\nEnter a prompt:")
        user_prompt = input(">> ")

        check_quit(user_prompt)
        if user_prompt == "":
            print("Prompt can not be empty. Type something!")
    
    return user_prompt


def query(client, llm_model, input_prompt):
    try:
        response = client.chat(model=llm_model, messages=[
        {
            'role': 'user',
            'content': input_prompt,
        },
        ])
        
    except ollama.ResponseError as e:
        print(f"[!] Error querying LLM {llm_model}: {e}. Trying .generate")
        try:
            response = client.generate(model=llm_model, prompt=input_prompt)
        except Exception as e:
            print(f"[!] Error querying LLM {llm_model}: {e}")
            return None
    except Exception as e:
        print(f"[!] Error querying LLM {llm_model}: {e}")
        return None
    
    return response


def setup_json():
    save_option = ""
    while save_option.lower() not in ["y", "yes", "n", "no"]:

        print("\nWould you like to save response(s) to a .json file? yes/no(y/n)")
        save_option = input(">> ")
        check_quit(save_option)
        if save_option in ["n", "no"]:
            return None
    
    print("Enter the name of the file (no spaces): ")
    filename = input(">> ").lower().strip().replace(" ", "")
    if ".json" not in filename:
        filename = f"{filename}.json"
    
    timestamp = datetime.now()
    filename = f"{timestamp.strftime('%Y-%m-%d_%H-%M')}_{filename}"

    return filename


def save_to_json(filename):
    global _in_memory_responses
    try:
        with open(filename, 'w') as f:
            json.dump(_in_memory_responses, f, indent=4)
        print(f"Responses saved to {filename}")
    except Exception as e:
        print(f"Error: Could not write to file {filename}: {e}")


def add_data(new_response):
    global _in_memory_responses
    try:
        _in_memory_responses.append(new_response)
    except Exception as e:
        print(f"[!] Error adding data: {e}")


def single_model(client, user_model):
    prompt = get_prompt()
    timestamp = datetime.now()
    reply = query(client, user_model, prompt)
    if reply and reply.message and reply.message.content:
        print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Response from {user_model}:\n{reply.message.content}\n")
        reply_msg = reply.message.content
    else:
        print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] No resposne from {user_model}")
        reply_msg = None
    
    add_data({"model": user_model,
            "timestamp": str(timestamp.strftime('%Y-%m-%d %H:%M:%S')),
            "response": reply_msg
            })


def all_models(client, models_list):
    prompt = get_prompt()
    for model_name in models_list:
        timestamp = datetime.now()
        reply = query(client, model_name, prompt)
        if reply and reply.message and reply.message.content:
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Response from {model_name}:\n{reply.message.content}\n")
            reply_msg = reply.message.content
        else:
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] No resposne from {model_name}")
            reply_msg = None
        
        add_data({"model": model_name,
                  "timestamp": str(timestamp.strftime('%Y-%m-%d %H:%M:%S')),
                  "response": reply_msg
                  })
        
        
        

if __name__ == "__main__":
    print("----- Welcome to OLLAMA LLMs -----\nType 'exit' to quit")

    ollama_host = os.getenv('OLLAMA_HOST')
    
    if ollama_host:
        print(f"Using OLLAMA_HOST env variable")
    else:
        print("OLLAMA_HOST environment variable not set. Defaulting to http://localhost:11434")
        # You can explicitly pass the host to ollama.Client if needed, e.g., client = ollama.Client(host=ollama_host or 'http://localhost:11434')
        # However, the library handles the environment variable automatically.

    try:
        # Initialize the Ollama client
        client = Client(
            host=f'http://{ollama_host}'
        )
        print("Sucessfully connected to host client")
    except Exception as e:
        print(f"[!] Error: Could not connect to Ollama host")
        print(f"Details {e}\nExiting program")
        sys.exit(1)
    
    try:
        models_obj_list = client.list()
        models_objects = models_obj_list.models
        models_names_list = [model_obj.model for model_obj in models_objects]
        print("Sucessfully found models")
    except Exception as e:
        print(f"[!] Error: Could not find models")
        print(f"Details {e}\nExiting program")
        sys.exit(1)

    
    mode = mode_menu()
    print_models(models_names_list)

    match mode:
        case "1":
            all_models(client, models_names_list)
        case "2":
            user_model = get_model(models_names_list)
            single_model(client, user_model)

    print("\n----- RESPONSES COMPLETED -----")

    filename = setup_json()
    if filename != None:
        save_to_json(filename)