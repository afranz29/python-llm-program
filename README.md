# Python LLM Program


## About

A program that uses the `ollama-python` library to interact with LLMs available on a host machine. A user can choose to input a prompt to either a selected model or all available models. The program will process the prompt and output the generated responses. Finally, users are given the option to save these responses to a .json file

## Installation

To get started with this program, you need to have Python installed on your machine. Then, install the required packages (see https://github.com/ollama/ollama-python):

```bash
pip install ollama
```

This program expects an environment variable `OLLAMA_HOST` containing the host machines address and port.

## Furture Updates
- skip embed models
- store results in a Pandas dataframe

__Last updated: 05/26/2025__