import os,glob
import email
import email.utils
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import string
from collections import Counter
import re

def url_extractor(raw_email):
    # eml = email.message_from_bytes(raw_email)
    eml = raw_email
            # Number of URLs in text/html section 
    html_payload = ""
    for part in eml.walk():
        if part.get_content_type() == "text/html":
            html_payload += part.get_payload(decode=True).decode('latin-1')     
    # Use BeautifulSoup to parse the HTML and extract all the URLs
    soup = BeautifulSoup(html_payload, "html.parser")
    urls = []
    for a_tag in soup.find_all('a', href=True):
        url = a_tag['href']
        # Remove any trailing spaces or punctuation marks
        url = re.sub('[\s\.\?,!]+$', '', url)
        if bool(re.search('https?:.',url)):
            urls.append(url)
    for a_tag in soup.find_all('a', attrs={"data-saferedirecturl": True}):
        url = a_tag['data-saferedirecturl']
        # Remove any trailing spaces or punctuation marks
        url = re.sub('[\s\.\?,!]+$', '', url)
        if bool(re.search('https?:.',url)):
            urls.append(url)
    return urls