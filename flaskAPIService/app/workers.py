# app/worker.py

from app import create_app
from app.googleCardScraperModule import run, GoogleBusinessCard
from . import mongo

app, celery = create_app()

@celery.task(name="scrape_site")
def scrape_site(url):
    gcards = run(url)  # This should return a list of GoogleBusinessCard objects

    # Update MongoDB
    db = mongo.cx.query_service

    for card in gcards:
        if isinstance(card, GoogleBusinessCard):
            db.query_gcard_results.insert_one(card.to_dict())

    return True
