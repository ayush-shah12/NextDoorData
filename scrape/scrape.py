import json
import math
import time
from functools import wraps
import logfire
from pydantic import ValidationError
from typing import List
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import csv
from keys import KEYS
from scrape.models import Business


def retry(retries=3, return_value=None):
    """Retry decorator"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:

                    return func(*args, **kwargs)
                except Exception as e:
                    logfire.error(f"Error in {func.__name__} {args} {e}")
                    if attempt < retries:
                        logfire.info(f"Retrying {func.__name__} {args} attempt {attempt + 1} of {retries}")

                        if func.__name__ == "get_businesses" or func.__name__ == "get_individual_businesses":
                            kwargs['use_premium'] = True
                            logfire.info(f"Retrying with PREMIUM for {func.__name__} {args} attempt {attempt + 1} of {retries}")
                        
                        time.sleep(3)
                    else:
                        logfire.error(f"MAJOR ERROR: ALL {retries} attempts failed for {func.__name__} {args} {e}")
            return return_value

        return wrapper

    return decorator


def fetch_data(url: str, use_premium: bool = False, render: bool = False) -> str:
    """Fetch data from url"""

    payload = {'api_key': KEYS.ScraperAPI.api_key, 'url': url}
   
    if render:
        payload['render'] = 'true'

    if use_premium:
        payload['premium'] = 'true'

    logfire.info(f"Fetching {url}")

    response = requests.get('https://api.scraperapi.com/', params=payload)
    response.raise_for_status()
    logfire.info(f"Successfully fetched {url}")
    return response.text


@retry(retries=3)
def get_businesses(city: str, state: str, category: str, use_premium=False) -> List[Business]:
    """Get businesses of a specific category in a specific city, state"""

    url: str = f"https://nextdoor.com/topics/{category}/{city}/{state}"

    response = fetch_data(url=url, use_premium=use_premium, render=False)
    soup = BeautifulSoup(response, 'html.parser')

    business_links = list(set([a["href"] for a in soup.find_all("a", href=True) if "/pages/" in a["href"]]))

    return [Business(next_door_url=link) for link in business_links]
    

@retry(retries=3)
def get_individual_businesses(business: Business, use_premium=False) -> Business:
    """Get individual businesses"""

    response = fetch_data(url=business.next_door_url, use_premium=use_premium, render=True)
    soup = BeautifulSoup(response, 'html.parser')

    name = soup.find("div", class_="name-selector").text.strip() if soup.find("div", class_="name-selector") else None
    street_address = soup.find("div", class_="street-address-selector").text.strip() if soup.find("div", class_="street-address-selector") else None
    city = soup.find("div", class_="city-selector").text.strip() if soup.find("div", class_="city-selector") else None
    state = soup.find("div", class_="state-selector").text.strip() if soup.find("div", class_="state-selector") else None
    zipcode = soup.find("div", class_="zip-code-selector").text.strip() if soup.find("div", class_="zip-code-selector") else None
    phone = soup.find("div", class_="phone-number-selector").text.strip() if soup.find("div", class_="phone-number-selector") else None
    email = soup.find("div", class_="email-selector").text.strip() if soup.find("div", class_="email-selector") else None
    website = soup.find("div", class_="website-url-selector").text.strip() if soup.find("div", class_="website-url-selector") else None

    categories_div = soup.find("div", class_="categories-selector")

    categories = [category.text.strip() for category in categories_div.find_all("div", class_="category-selector")]

    business.name = name
    business.street = street_address
    business.city = city
    business.state = state
    business.zip_code = zipcode
    business.phone = phone
    business.email = email
    business.website = website
    business.categories = categories

    return business
