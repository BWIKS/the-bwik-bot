import os
from typing import Optional

from utils.http_utils import fetch_url_content
from dotenv import load_dotenv

load_dotenv()

local = os.getenv('LOCAL')

prompts_url = "https://raw.githubusercontent.com/BWIKS/the-bwik-bot/main/prompts/"

async def fetch_context(file_name: str, bot_number: Optional[str] = None) -> str:
    if bot_number:
        location = f"bot-{bot_number}/{file_name}.txt"
    else:
        location = f"{file_name}.txt"

    if local == "true":
        with open(f"prompts/{location}", 'r') as file:
            context = file.read()
    else:
        url = f"{prompts_url}{location}"
        context = await fetch_url_content(url)
    return context
