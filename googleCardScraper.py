import playwright
from playwright.sync_api import Page, sync_playwright

import locators
from locators import *
from utils import scroll_to_load_data
from typing import List


class GoogleBusinessCard():
    def __init__(self, name=None, address=None, website=None, phone=None):
        self.name = name
        self.address = address
        self.website = website
        self.phone = phone

    def to_dict(self):
        return vars(self)


def endcon(pageed):
    pageed.locator("//span[contains(text(), \"You've reached the end of the list.\")]").is_visible()


def googleCardScraper(url, page: Page) -> List[GoogleBusinessCard]:
    """
    Returns a list of Google Business Cards from a given page URL and browser Instance
    :param url: URL with Query
    :param page: Browser Instance with already created context
    :return:
    """
    page.goto(url, wait_until="load")

    # pull in all the data through scrolling can remove contains(@class, 'dS8AEf') if needed
    scroll_to_load_data(page,
                        scroll_selector="//*[contains(@class, 'dS8AEf') and @tabindex and @role='feed']",
                        endCon=lambda: endcon(page))

    all_business_cards = page.locator(locators.business_cards_locator)
    for i in range(all_business_cards.count()):
        all_business_cards.nth(i).click()
        # Pull data
        modal = page.locator(locators.business_card_modal)
        print(modal.text_content())



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
