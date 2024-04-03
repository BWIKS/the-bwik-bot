import os
import openai
import telegram
import asyncio
from datetime import datetime
import requests

from openai import OpenAI
from telethon.sync import TelegramClient
from utils.fetch_context import fetch_context

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')
chat_id = int(os.getenv('TELEGRAM_CHAT_ID'))
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
bot_name = os.getenv('BOT_NAME')
bot_choice = os.getenv('BOT_CHOICE')
debug = os.getenv('DEBUG')

client = OpenAI()
openai.api_key = openai_api_key

bot = telegram.Bot(token=bot_token)

async def get_messages(limit) -> list[str]:
    usernames = {}

    client = TelegramClient('sync', api_id, api_hash)
    await client.start(phone_number)
    try:
        chat_entity = await client.get_entity(chat_id)
        messages = []
        async for message in client.iter_messages(chat_entity, limit=limit):
            print(message)
            from_id = message.from_id.user_id if message.from_id else None
            if from_id:
                if from_id not in usernames:
                    user = await client.get_entity(from_id)
                    if user.username: 
                        usernames[from_id] = user.username
                    else: 
                        usernames[from_id] = user.first_name
            
            # Ensure from_id exists in usernames and message.text is not None
            if from_id in usernames and message.text:
                messages.append(usernames[from_id] + ' : ' + message.text)
    finally:
        await client.disconnect()
    return messages

async def bot_action() -> None:
    print('Reading messages...')
    messages = await get_messages(10)
    messages.reverse()

    lastMessage = messages[-1]
    print(lastMessage)
    if bot_name in lastMessage.split(':')[0]: return False

    context = (await fetch_context('message-type')) + '\n' + lastMessage
    
    if(debug == "true"):
        print('------')
        print('---1st-prompt---')
        print(context)
        print('------')
        print('------')


    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context}
        ]
    )

    if(debug == "true"):
        print('Message type: ', response.choices[0].message.content.lower())

    context = await fetch_context('context-' + response.choices[0].message.content.lower(), bot_choice)

    context += '\n\n --- Messages history --- \n\n' + '\n'.join(messages[:-1])
    context = context.replace('{BOT_NAME}', bot_name)

    if(debug == "true"):
        print('------')
        print('---2nd-prompt---')
        print(context)
        print('------')
        print('------')


    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": lastMessage}
        ]
    )

    context = await fetch_context('text-to-bwik')
    context = context + response.choices[0].message.content

    url = 'https://raw.githubusercontent.com/BWIKS/bwiks-glossary/main/definitions.json'
    response = requests.get(url)
    data = response.json()
    context += '\n\n --- Definitions --- \n\n'
    for item in data['definitions']:
        context += f"Word: {item['word']}\n"
        context += f"Type: {item['type']}\n"
        context += f"Definition: {item['definition']}\n"

    if(debug == "true"):
        print('------')
        print('---3rd-prompt---')
        print(context)
        print('------')
        print('------')

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context}
        ]
    )

    print('Sent ', response.choices[0].message.content.lower())

    if ('nothing' in response.choices[0].message.content.lower()): return False
    else: await bot.send_message(chat_id, response.choices[0].message.content)

async def main() -> None:
    await bot_action()

if __name__ == "__main__":
    asyncio.run(main())
