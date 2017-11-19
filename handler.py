import sys
import logging
import os
import uuid
import boto3
import random

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

random_responses = [
    "Stay low, stay quiet, keep it simple, don't expect too much, enjoy what you have",
    "We are what we repeatedly do. Greatness then, is not an act, but a habit",
    "It takes billions of years to create a human being. And it takes only a few seconds to die",
    "All I know is that I do not know anything", "It comes from within.", "Never laugh at live dragons",
    "Be wise today so you don't cry tomorrow.", "There is nothing like a crisis to define who you are.",
    "Success is getting what you want. Happiness is liking what you get",
    "Those who are wise won't be busy, and those who are too busy can't be wise",
    "You're too young to decide to live forever.", "One person's greatest regret is another person's greatest memory",
    "Count your age by friends, not years. Count your life by smiles, not tears",
    "I have found that if you love life, life will love you back", "No way!", "Come on!", "What did you just say?",
    "Life is really simple, but we insist on making it complicated", "Go on", "Are you serious?",
    "I may be naked, but my thoughts are still hidden",
]


def _get_data(event):
    from_data = event['message']['from']
    fields = ['id', 'first_name', 'last_name', 'username', 'language_code']
    item = {k: from_data.get(k, '-') for k in fields}
    item.update({'date': event['message'].get('date'), 'text': event['message'].get('text'), 'key': str(uuid.uuid1())})
    if item.get('username') == '-':
        item.update({'username': str(uuid.uuid1())})
    return item.copy()


def receive(event, context):
    response = {"statusCode": 200, 'authorize': 0}
    try:

        message = str(event["message"]["text"])

        if message and message.startswith('/start'):
            command, user_id = message.split(' ')
            response.update({'user_id': int(user_id)})
            response.update({'authorize': 1})

    except Exception as e:
        logger.exception(e)

    return response


def respond(event, context):

    chat_id = event["message"]["chat"]["id"]
    first_name = event["message"]["chat"].get("first_name", "Bro")
    text = event['message'].get('text')

    response = random.choice(random_responses)
    results = event.get("results")
    if results and results.get('authorize'):
        response = results.get('authorize').get("message")

    if any(map(lambda w: w in text, ['hi', 'hello', 'hey'])):
        response = "Hi {}".format(first_name)

    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    requests.post(url, data)

    return {"statusCode": 200}


def log(event, context):
    table = dynamodb.Table(os.environ['MESSAGES_TABLE'])
    table.put_item(Item=_get_data(event))
    return {"statusCode": 200}


def authorize(event, context):

    message = "Authorization is successful"

    table = dynamodb.Table(os.environ['USERS_TABLE'])
    chat_id = event["message"]["chat"]["id"]
    user_id = event['results']['receive']['user_id']
    data = {"chat_id": chat_id, 'user_id': user_id}
    # send data to your website to auth
    all_data = _get_data(event)
    item = {k: all_data.get(k) for k in ['id', 'first_name', 'last_name', 'username', 'language_code']}

    item.update(data)
    table.put_item(Item=item)

    return {"statusCode": 200, "message": message}
