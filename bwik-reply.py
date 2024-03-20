import os
import openai
from collections import deque

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from openai import OpenAI
from utils.http_utils import fetch_url_content

# Load environment variables
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

client = OpenAI()

# Set the OpenAI API key
openai.api_key = openai_api_key

# Initialize a deque to store the last 20 messages
message_history = deque(maxlen=20)

prompts_url = "https://raw.githubusercontent.com/BWIKS/the-bwik-bot/main/prompts/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Chat ID: {update.effective_chat.id}")    
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assistant_context = await fetch_url_content(prompts_url + 'context-bwik.txt')


    # Update message history
    assistant_context = '\n'.join([assistant_context, "Message history:"] + [str(message) for message in message_history])

    user_message = update.message.text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": assistant_context},
            {"role": "user", "content": update.effective_user.first_name + ": " + user_message}
        ]
    )
    await update.message.reply_text(response.choices[0].message.content)
    
    message_history.append(update.effective_user.first_name + ": " + update.message.text)
    if(response):
        message_history.append("Assistant: " + response.choices[0].message.content)


def main() -> None:
    application = Application.builder().token(telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    application.run_polling()

if __name__ == "__main__":
    main()
