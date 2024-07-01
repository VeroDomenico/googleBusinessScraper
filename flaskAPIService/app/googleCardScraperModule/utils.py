import random
import time


def scroll_to_load_data(page, scroll_selector, endCon, timeOut=60000):
    """
    Takes in page and selector and scroll till break condition of no change
    :param endCon: function to end the scrolling
    :param page: Playwright Page Obj
    :param scroll_selector: Scroll Selector
    :param timeOut: Timeout in milliseconds
    :return:
    """
    start_time = time.time()
    scroll = page.locator(scroll_selector)

    while True:
        # Scroll down the table
        scroll_distance = random.randint(300, 800)  # Adjust range for more variability
        scroll.evaluate(f"el => el.scrollBy(0, {scroll_distance})")

        # Wait for data to load
        page.wait_for_timeout(1000)

        # Check if the end condition is met
        if endCon():
            break

        # Check if the timeout has been exceeded
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        if elapsed_time > timeOut:
            print("Scrolling timeout exceeded")
            break
