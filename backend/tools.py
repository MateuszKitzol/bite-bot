import os
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from langchain_core.tools import tool
from pydantic import SecretStr
from dotenv import load_dotenv

# Correctly load the .env file from the backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

USDA_API_KEY = SecretStr(os.environ["USDA_API_KEY"])

@tool
async def add(x: float, y: float) -> float:
    """Add 'x' and 'y'."""
    return x + y

@tool
async def final_answer(answer: str, tools_used: list[str]) -> dict[str, str | list[str]]:
    """Use this tool to provide a final answer to the user."""
    return {"answer": answer, "tools_used": tools_used}

@tool
async def teleman_movies_today() -> list[dict]:
    """Scrapes teleman.pl/filmy for movies showing today.
    Returns a list of dictionaries with 'title', 'time', and 'channel'.
    """
    url = "https://www.teleman.pl/filmy"
    movies_today = []
    today_str = datetime.now().strftime("%d.%m") # Format: DD.MM

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()  # Raise an exception for bad status codes
            html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')

    for movie_item in soup.find_all('a', class_='movie-search-item'):
        title_tag = movie_item.find('h3', class_='title')
        airing_div = movie_item.find('div', class_='airing')

        if title_tag and airing_div:
            airing_children = airing_div.find_all('div')
            if len(airing_children) >= 3:
                date_text = airing_children[1].get_text(strip=True)
                time_text = airing_children[2].get_text(strip=True)
                channel_figure = airing_children[0].find('figure')
                channel_name = "Unknown Channel"
                if channel_figure and 'background-image' in channel_figure.get('style', ''):
                    style = channel_figure['style']
                    # Extract URL from style and then filename
                    import re
                    match = re.search(r'url\((.*?)\)', style)
                    if match:
                        img_url = match.group(1)
                        channel_name = os.path.splitext(os.path.basename(img_url))[0]

                # Check if the movie is for today
                if "Dziś" in date_text or today_str in date_text:
                    movies_today.append({
                        "title": title_tag.get_text(strip=True),
                        "time": time_text,
                        "channel": channel_name
                    })
    return movies_today

@tool
async def get_food_nutrients(query: str) -> list[dict]:
    """
    Searches for a food item and returns its nutritional information.
    """
    api_key = USDA_API_KEY.get_secret_value()
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()

    if data.get("foods"):
        # Return nutrients of the first food item
        return data["foods"][0].get("foodNutrients", [])
    return []