import os
import aiohttp
import asyncio
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
async def get_food_nutrients(ingredients: list[str]) -> dict[str, list[dict]]:
    """
    Searches for a list of food items and returns their nutritional information.
    It prioritizes the 'Foundation' dataType for the search.
    Returns a dictionary where keys are the ingredients and values are their nutritional information.
    """
    api_key = USDA_API_KEY.get_secret_value()
    results = {}

    async def fetch_nutrient(session, ingredient):
        # First, try to find the ingredient with 'Foundation' dataType
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={ingredient}&dataType=Foundation"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("foods"):
                    return {ingredient: data["foods"][0].get("foodNutrients", [])}

            # If no 'Foundation' food is found, search without the dataType parameter
            url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={ingredient}"
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("foods"):
                    return {ingredient: data["foods"][0].get("foodNutrients", [])}

            return {ingredient: []}
        except aiohttp.ClientError as e:
            return {ingredient: f"Error fetching data: {e}"}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_nutrient(session, ingredient) for ingredient in ingredients]
        nutrient_results = await asyncio.gather(*tasks)

    for res in nutrient_results:
        results.update(res)

    return results
