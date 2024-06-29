import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailExtractJob:
    def __init__(self, parent_id, entry):
        self.parent_id = parent_id
        self.entry = entry
        self.url = entry['website']
        self.max_retries = 0
        self.priority = 'high'

    def fetch_page(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching the URL: {e}")
            return None

    def extract_emails(self, content):
        emails = set()
        
        soup = BeautifulSoup(content, 'lxml')
        for script_or_style in soup(['script', 'style', 'img', 'video', 'audio']):
            script_or_style.decompose()
        
        # Extract emails from mailto links
        for mailto in soup.select('a[href^=mailto]'):
            email = mailto.get('href').replace('mailto:', '')
            valid_email = self.get_valid_email(email)
            if valid_email:
                emails.add(valid_email)
        
        # Extract emails using regex
        emails.update(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.text))
        print(emails)
        return list(emails)

    def get_valid_email(self, email):
        email = email.strip()
        if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
            return email
        return None

    def process(self):
        logger.info(f"Processing email job for URL: {self.url}")
        content = self.fetch_page()
        if not content:
            return self.entry, None, None
        
        emails = self.extract_emails(content)
        self.entry['emails'] = emails
        return self.entry, None, None

    def process_on_fetch_error(self):
        return True

# Example usage
if __name__ == "__main__":
    entry = {'website': 'https://example.com'}
    job = EmailExtractJob(parent_id='1234', entry=entry)
    result, _, _ = job.process()
    print(result)
