import openai
import numpy as np
from embeddings import query_all
import os
import ast
from server import app

openai.api_key = app.config.get("OPENAI_API_KEY")

MODEL = "gpt-3.5-turbo"

def openai_response(context, email):
    """generate a response from openai
    """
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an organizer for HackMIT who is responding to an email from a participant. \
             Please write an email response to the participant. Begin the email with the header 'Dear Participant' and end the email with footer 'Best regards, The HackMIT Team'. \
             You receive documents to help you answer the email. Please do not include information that is not explicitly stated in the documents. If possible, keep responses brief."},
            *context,
            {"role": "user", "content": email}
        ]
    )
    return response['choices'][0]['message']['content']

def openai_parse(email):
    """parse an email using openai
    """
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an organizer for HackMIT. Please parse incoming emails from participants into separate questions. Return a list of questions in the format of a python list."},
            {"role": "user", "content": email}
        ]
    )
    return ast.literal_eval(response['choices'][0]['message']['content'])

def generate_context(email):
    """generate email context
    """
    questions = openai_parse(email)
    context = []

    results = query_all(3, questions)
    for result in results:
        print("query:", result['query'])
        message = ""
        for doc in result['result']:
            print("confidence:", doc['score'])
            print(f"Q: {doc['question']}")
            print(f"A: {doc['answer']}")
            message += doc['question'] + " " + doc['answer'] + "\n"
        print()
        context.append({"role": "system", "content": message})

    return context

def generate_response(email):
    """generate response to email
    """
    context = generate_context(email)
    response = openai_response(context, email)
    return response

if __name__=='__main__':
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    response = generate_response("Hii \
I am Hariom and I am from Bharat so I have a question about competition mode, Is it also held online or hybrid? \
Actually I am enthusiastic to learn new skills. If you do also organize a hackathon or competition regarding us please let me know.\
Thank You")
    print(response)
