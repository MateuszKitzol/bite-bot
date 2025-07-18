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
async def final_answer(answer: str, tools_used: list[str]) -> dict[str, str | list[str]]:
    """Use this tool to provide a final answer to the user."""
    return {"answer": answer, "tools_used": tools_used}

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