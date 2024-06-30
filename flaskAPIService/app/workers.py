import os
import time

from celery import Celery
from app.googleCardScraperModule import run


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("REDIS_URL")
celery.conf.result_backend = os.environ.get("REDIS_URL")


@celery.task(name="scrape_site")
def scrape_site(url):
    gcards = run(url)  

    # Update Mongo DB
    for gcard in gcards:
        print(gcard.to_dict())
    return True