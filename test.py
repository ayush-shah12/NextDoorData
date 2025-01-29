from scrape.scrape import get_businesses, get_individual_businesses
from scrape.models import Business


businesses: list[Business] = get_businesses("anchorage", "ak", "general-contractor")

for business in businesses:
    a: Business = get_individual_businesses(business)
    print(a)
    break