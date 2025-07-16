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

async def _get_nutrient_details(session, api_key, ingredient, data_type=None):
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={ingredient}"
    if data_type:
        search_url += f"&dataType={data_type}"

    async with session.get(search_url) as response:
        response.raise_for_status()
        data = await response.json()
        if data.get("foods"):
            fdcId = data["foods"][0].get("fdcId")
            if fdcId:
                details_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdcId}?api_key={api_key}&format=abridged"
                async with session.get(details_url) as details_response:
                    details_response.raise_for_status()
                    details_data = await details_response.json()
                    return details_data.get("foodNutrients", [])
    return None

@tool
async def get_food_nutrients(ingredients: list[str]) -> dict[str, list[dict]]:
    """
    Searches for a list of food items and returns their full nutritional information.
    It prioritizes the 'Foundation' dataType for the search.
    Returns a dictionary where keys are the ingredients and values are their nutritional information.
    """
    api_key = USDA_API_KEY.get_secret_value()
    results = {}

    async def fetch_nutrient(session, ingredient):
        try:
            # First, try to find the ingredient with 'Foundation' dataType
            nutrients = await _get_nutrient_details(session, api_key, ingredient, "Foundation")

            # If no 'Foundation' food is found, search without the dataType parameter
            if nutrients is None:
                nutrients = await _get_nutrient_details(session, api_key, ingredient)

            return {ingredient: nutrients if nutrients is not None else []}
        except aiohttp.ClientError as e:
            return {ingredient: f"Error fetching data: {e}"}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_nutrient(session, ingredient) for ingredient in ingredients]
        nutrient_results = await asyncio.gather(*tasks)

    for res in nutrient_results:
        results.update(res)

    return results

@tool
async def calculate_meal_nutrition(ingredients_nutrition: dict[str, list[dict]], amounts: dict[str, float]) -> dict[str, dict[str, float | str]]:
    """
    Calculates the total nutritional value of a meal based on a list of ingredients and their amounts.
    The amounts are in grams.
    """
    total_nutrition = {}

    for ingredient, nutrients in ingredients_nutrition.items():
        amount_in_grams = amounts.get(ingredient, 0)
        if not nutrients or amount_in_grams == 0:
            continue

        for nutrient in nutrients:
            nutrient_name = nutrient.get("name")
            nutrient_amount = nutrient.get("amount", 0)
            nutrient_unit = nutrient.get("unitName", "g")

            # Assuming the nutrient amount is per 100g
            amount_per_gram = nutrient_amount / 100
            total_amount = amount_per_gram * amount_in_grams

            if nutrient_name in total_nutrition:
                total_nutrition[nutrient_name]["amount"] += total_amount
            else:
                total_nutrition[nutrient_name] = {"amount": total_amount, "unit": nutrient_unit}

    return total_nutrition
