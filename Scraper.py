import json
import random
import sys

import time

from playwright.sync_api import sync_playwright, Page

"""
Locators
"""

business_card: str = "//div[contains(@class, 'fontBodyMedium') and .//span]"



def route_intercept(route):
    if route.request.resource_type == "image":
        print(f"Blocking the image request to: {route.request.url}")
        return route.abort()
    return route.continue_()
proxy = "104.167.24.197:3128"


if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False,
        #                                     proxy={
        #     'server': f'http://{proxy}',
        # }
                                            )
        context = browser.new_context()
        page = context.new_page()

        query = "optometrist"
        # page.route("**/*", route_intercept)
        page.goto(f"https://www.google.com/maps/search/{query}")

        scroll = page.locator(".dS8AEf").nth(1)
        start_time = time.time()
        timeOut = 50

        scroll = page.locator(".dS8AEf").nth(1)
        timeOut = 50
        start_time = time.time()

        while timeOut > 0:
            # Check if the specified element is visible
            if page.locator("//span[contains(text(), \"You've reached the end of the list.\")]").is_visible():
                break

            # Emulate human-like scroll interaction with random distance and small random delay
            scroll_distance = random.randint(300, 800)  # Adjust range for more variability
            scroll.evaluate(f"el => el.scrollBy(0, {scroll_distance})")

            # Add a random sleep time to emulate human pause after scrolling
            time.sleep(random.uniform(0.2, 0.5))  # Random delay between 0.2 and 0.5 seconds

            # Calculate the elapsed time and update the timeout
            elapsed_time = time.time() - start_time
            timeOut -= elapsed_time

            # Reset the start time for the next iteration
            start_time = time.time()



        # all_business_card = page.locator(business_card)
        # print("DoneP Pulling Data")
        # for i in range(all_business_card.count()):
        #     card = {}
        #     print(all_business_card.count())
        #     try:
        #         business_header = all_business_card.nth(i)
        #     except:
        #         business_header = "Unable to Pull Business Name"
        #     try:
        #         rating = all_business_card.nth(i).locator("ZkP5Je").get_attribute("aria-label")
        #     except:
        #         rating = "N/A"
        #     try:
        #         phone = all_business_card.nth(i).locator("UsdlK").text_content()
        #     except:
        #         phone = "N/A"
        #     card["business_name"] = business_header
        #     card["rating"] = rating
        #     card["phone"] = phone
        #     dict[f"card_{i}"] = card
        #     print(card)
        # print(dict)
    sys.exit(0)