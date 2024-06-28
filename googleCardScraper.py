import re

import playwright
from playwright.sync_api import Page, sync_playwright

import locators
from locators import *
from utils import scroll_to_load_data
from typing import List
import time


class GoogleBusinessCard():
    def __init__(self, name=None,review_count=None, rating=None, address=None, website=None, phone=None):
        self.name = name
        self.rating = rating
        self.review_count = review_count
        self.address = address
        self.website = website
        self.phone = phone

    def to_dict(self):
        return vars(self)

# Helpers
def clean_data(value):
    return re.sub(r'[^a-zA-Z0-9\s()]', '', value)

def endcon(pageed):
    pageed.locator("//span[contains(text(), \"You've reached the end of the list.\")]").is_visible()


def googleCardScraper(url, page: Page) -> List[GoogleBusinessCard]:
    """
    Returns a list of Google Business Cards from a given page URL and browser Instance
    :param url: URL with Query
    :param page: Browser Instance with already created context
    :return:
    """

    # vars
    googleBusinessCards = []

    # Logic

    page.goto(url, wait_until="load")

    # # pull in all the data through scrolling can remove contains(@class, 'dS8AEf') if needed
    # scroll_to_load_data(page,
    #                     scroll_selector="//*[contains(@class, 'dS8AEf') and @tabindex and @role='feed']",
    #                     endCon=lambda: endcon(page))

    all_business_cards = page.locator(locators.business_cards_locator)
    for i in range(all_business_cards.count()):
        all_business_cards.nth(i).click()
        time.sleep(0.5)

        # Pull data
        modal = page.locator(locators.business_card_modal)
        googleBusinessCard = GoogleBusinessCard()
        time.sleep(.25)

        # Get rating
        if page.locator("//span[contains(@class,'ceNzKf')]").is_visible():
            try:
                googleBusinessCard.rating = page.locator("//span[contains(@class,'ceNzKf')]").get_attribute('aria-label')
            except:
                print("Unable to pull rating")

            try:
                googleBusinessCard.review_count= page.locator("//div[contains(@class,'F7nice')]//span[@aria-label]").nth(1).text_content()
            except:
                print("Unable to pull review count")
        else:
            googleBusinessCard.review_count = "No Results or N/A"
            googleBusinessCard.rating = "No Results or N/A"

        # Get Company Name
        try:
            googleBusinessCard.name = modal.locator("//h1[contains(@class,'DUwDvf')]").inner_text().strip()
        except:
            print("Unable to pull name")
       # "button", class_ = "CsEnBe"
        # Get address
        import re

        # Function to remove non-alphanumeric characters except parentheses
        def clean_data(value):
            return re.sub(r'[^a-zA-Z0-9\s()]', '', value)

        try:
            phone_raw = page.locator(
                "//*[@data-tooltip='Copy phone number' and @class='CsEnBe']").text_content().strip()
            googleBusinessCard.phone = clean_data(phone_raw)
        except:
            print("Unable to pull phone number")

        try:
            website_raw = page.locator("//*[@data-tooltip='Open website' and @class='CsEnBe']").text_content().strip()
            googleBusinessCard.website = clean_data(website_raw)
        except:
            print("Unable to pull website")

        try:
            address_raw = page.locator("//*[@data-tooltip='Copy address' and @class='CsEnBe']").text_content().strip()
            googleBusinessCard.address = clean_data(address_raw)
        except:
            print("Unable to pull address")

        # Get Phone number

        # all_info_bars = modal.query_selector_all("button.CsEnBe")
        googleBusinessCards.append(googleBusinessCard)
    for gcard in googleBusinessCards:
        print(gcard.to_dict())
    print(googleBusinessCards)
    return None


if __name__ == "__main__":
    """
    Test Driver
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        googleCardScraper(f"https://www.google.com/maps/search/optometrist", page)
