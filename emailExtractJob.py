import requests
from bs4 import BeautifulSoup
import re
import logging
from lxml import etree
from logging.handlers import RotatingFileHandler
from email_validator import validate_email
from urllib.parse import urljoin, urlparse, urlunparse

# Configure logging
LOG_FILENAME = 'email_extractor.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

# Configure root logger
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
# do this on env var prod or local
# logging.basicConfig(level=logging.LOG, format=LOG_FORMAT)

# Create file handler which logs even debug messages
file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
file_handler.setLevel(logging.DEBUG)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Create formatter and add it to the handlers
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class EmailExtractJob:
    def __init__(self, parent_id, entry, depth=1):
        self.parent_id = parent_id
        self.entry = entry
        self.url = entry['website']
        self.depth = depth
        self.max_retries = 0
        self.priority = 'high'
        self.email_found = False
        self.socials = []

    def fetch_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(url, headers=headers,timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            logger.debug(f"Successfully fetched page: {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching the URL: {e}")
            return None

    def extract_emails(self, content):
        emails = set()

        logger.debug(f"Content length: {len(content)}, Content start: {content[:100]}")

        # Extract emails from mailto links
        for mailto in BeautifulSoup(content, 'lxml').select('a[href^=mailto]'):
            email = mailto.get('href').replace('mailto:', '')
            valid_email = self.get_valid_email(email)
            if valid_email:
                emails.add(valid_email)
        
        # Extract emails using regex
        possible_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        for email in possible_emails:
            valid_email = self.get_valid_email(email)
            if valid_email:
                emails.add(valid_email)
        
        logger.debug(f"Extracted emails: {emails}")
        return list(emails)

    def get_valid_email(self, email):
        if not isinstance(email, str):
            return None
        
        try:
            # Validate the email address using the email-validator library
            valid_email = validate_email(email)
            email = valid_email.email.lower()
            if re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$', email):
                return email
        except:
            # If the email address is not valid, skip it
            return None

        return None

    def extract_social_links(self, content):
        social_links = set()

        soup = BeautifulSoup(content, 'lxml')
        for link in soup.find_all('a', href=True):
            link_url = link.get('href')

            # Check for common social media platforms
            for platform in ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'x.com', 'yelp.com']:
                if platform in link_url:
                    # If social media platform is found in the link, add to the set
                    social_links.add(link_url.strip())
        logger.debug(f"Extracted social links: {social_links}")
        return list(social_links)
    
    def clean_url(self, url):
        parsed_url = urlparse(url)
        cleaned_path = parsed_url.path.replace('%0A', '').replace('%20', '').strip()
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, cleaned_path, parsed_url.params, parsed_url.query, parsed_url.fragment))
        return cleaned_url

    def fetch_sitemap(self, url):
        try:
            response = requests.get(url)
            logger.debug(f"Fetching sitemap at {url}, HTTP status: {response.status_code}")
            if response.status_code == 200:
                try:
                    logger.debug(f"Successfully fetched sitemap: {url}")
                    return etree.fromstring(response.content)
                except etree.XMLSyntaxError as e:
                    logger.error(f"XML parsing error: {e}")
                    return None
            else:
                logger.error(f"No sitemap XML found at {url}")
                return None
        except Exception as e:
            logger.error(f"Error fetching sitemap: {e}")
            return None

    def extract_emails_from_map(self, xmlmap, current_depth):
        if current_depth > self.depth or self.email_found:
            logger.debug(f"Current depth: {current_depth}, Email found status: {self.email_found}")
            return set()

        priority_pages = ['about', 'about-us', 'contact', 'contact-us']
        urls = []

        if xmlmap.tag.endswith("sitemapindex"):
            for sitemap in xmlmap.findall("{*}sitemap"):
                new_sitemap = self.fetch_sitemap(sitemap.find("{*}loc").text)
                if new_sitemap is not None:
                    emails = self.extract_emails_from_map(new_sitemap, current_depth + 1)
                    if emails:
                        return emails
        elif xmlmap.tag.endswith("urlset"):
            for url in xmlmap.findall("{*}url"):
                loc = url.find("{*}loc").text
                for page in priority_pages:
                    if page in loc.lower():
                        urls.insert(0, loc)  # Prioritize adding priority pages
                        break
                else:
                    urls.append(loc)

            for page_url in urls:
                if self.email_found:
                    break
                cleaned_url = self.clean_url(page_url)
                page = self.fetch_page(cleaned_url)
                if page is not None:
                    soup = BeautifulSoup(page, 'lxml')
                    for script_or_style in soup(['script', 'style', 'img', 'video', 'audio']):
                        script_or_style.decompose()
                    emails = self.extract_emails(soup.text)
                    if emails:
                        self.email_found = True
                        return emails

        return set()

    def process(self):
        logger.info(f"Processing email job for URL: {self.url}")
        content = self.fetch_page(self.url)
        emails = self.extract_emails(content) if content else []

        if not emails:
            logger.info(f"No emails found on the main page, checking sitemap.")
            sitemap_url = self.url + '/sitemap.xml'
            sitemap = self.fetch_sitemap(sitemap_url)
            if sitemap is not None:
                emails = self.extract_emails_from_map(sitemap, current_depth=self.depth)

        social_links = self.extract_social_links(content) if content else []
        
        self.socials = social_links
        logger.info(f"Emails found: {emails}")
        logger.info(f"Social links found: {social_links}")
        return emails, self.socials, None

# Example usage
if __name__ == "__main__":
    entry = {'website': 'https://visionsource-viera.com'}
    job = EmailExtractJob(parent_id='1234', entry=entry, depth=2)
    result, _, _ = job.process()
    print(result)
