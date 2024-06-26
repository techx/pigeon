"""Responses.

This module is used to generate responses to incoming emails using OpenAI.
"""

import ast
from typing import cast

import numpy as np
import openai
from openai.types.chat import ChatCompletionMessageParam

from server.config import OPENAI_API_KEY, OpenAIMessage, RedisDocument
from server.nlp.embeddings import query_all
from server.utils import custom_log

openai.api_key = OPENAI_API_KEY

MODEL = "gpt-4o"


def openai_response(thread: list[OpenAIMessage], sender: str) -> str:
    """Generate a response from OpenAI.

    Args:
        thread: previous email thread
        sender: hacker email address

    Returns:
        email response generated by
    """
    messages = [
        {
            "role": "system",
            "content": f"You are an organizer for HackMIT. You are responsible for \
            responding to an email from a participant. \
            Please write an email response to the participant. Begin the email with \
            the header 'Dear [First Name]' where '[First Name]' is the participant's \
            first name and end the email with the footer 'Best regards, The \
            HackMIT Team'. Do not include the subject line in your response. \
            The participant's email address is {sender}.\
            You receive documents to help you answer the email. \
            Please do not include information that is not explicitly stated in the \
            documents. It is very important to keep responses brief and only answer \
            the questions asked. However, please write the emails in a friendly \
            tone.",
        }
    ]
    messages += thread

    messages += [
        {
            "role": "system",
            "content": "Once again, please do not include information that is not \
            explicitly stated in the documents. It is very important to keep responses \
            brief and only answer the questions asked. Please write the emails in a \
            friendly tone.",
        }
    ]

    messages = cast(list[ChatCompletionMessageParam], messages)
    response = openai.chat.completions.create(model=MODEL, messages=messages)

    if response.choices[0].message.content is None:
        return "openai unknown error"

    return response.choices[0].message.content


def openai_parse(email: str) -> list[str]:
    """Parse an email into questions using OpenAI.

    Args:
        email: hacker email

    Returns:
        list of questions parsed from the email
    """
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an organizer for HackMIT. Please parse incoming \
                    emails from participants into separate questions. Return a list of \
                    questions in the format of a python list.",
            },
            {"role": "user", "content": email},
        ],
    )
    try:
        questions = ast.literal_eval(cast(str, response.choices[0].message.content))
        assert isinstance(questions, list)
        assert len(questions) > 0
        return questions
    except Exception as e:
        custom_log(
            "open ai parsed email as '",
            response.choices[0].message.content,
            "', resulting in error '",
            e,
            "'. returning entire email as a single question instead.",
        )
        return [email]


def confidence_metric(confidences: list[float]) -> float:
    """Compute confidence metric for a list of confidences.

    Args:
        confidences: list of confidences

    Returns:
        confidence metric
    """
    custom_log("confidences", confidences)
    return np.min(np.array(confidences))


def generate_context(
    email: str,
) -> tuple[list[OpenAIMessage], dict[str, list[RedisDocument]], float]:
    """Generate email context.

    Args:
        email: hacker email

    Returns:
        (list of contexts for all questions in email,
        dictionary mapping each question to list of context documents used to
        answer question,
        confidence metric for all documents)
    """
    questions = openai_parse(email)
    confidences = []
    contexts = []
    docs = {}

    results = query_all(3, questions)
    message = "Here is some context to help you answer this email: \n"
    for result in results:
        confidence = 0
        docs[result["query"]] = []
        for doc in result["result"]:
            confidence = max(confidence, doc["score"])
            message += doc["question"] + " " + doc["content"] + "\n"
            docs[result["query"]].append(doc)
        confidences.append(confidence)

    contexts.append({"role": "system", "content": message})
    return contexts, docs, confidence_metric(confidences)


def generate_response(
    sender: str, email: str, thread: list[OpenAIMessage] | None = None
) -> tuple[str, dict[str, list[RedisDocument]], float]:
    """Generate response to email.

    Args:
        sender: hacker email address
        email: newest incoming hacker email
        thread : previous email thread

    Returns:
        (email response,
        dictionary mapping each question to list of context documents used to
        answer question,
        confidence of response)
    """
    if thread is None:
        thread = []

    # generate new context
    contexts, docs, confidence = generate_context(email)

    # generate new response
    thread.append({"role": "user", "content": email})
    thread += contexts
    return openai_response(thread, sender), docs, confidence
