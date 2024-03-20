import os

from utils.http_utils import fetch_url_content
from dotenv import load_dotenv

load_dotenv()

local = os.getenv('LOCAL')

prompts_url = "https://raw.githubusercontent.com/BWIKS/the-bwik-bot/main/prompts/"

async def fetch_context(file_name: str) -> str:
    if (local == "true"):
        with open(f"prompts/{file_name}.txt", 'r') as file:
            context = file.read()
    else: context = await fetch_url_content(prompts_url + f"{file_name}.txt")
    return context
