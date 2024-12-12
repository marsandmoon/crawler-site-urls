import signal
import sys
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque

# 所有资源
website_url = "https://mingdao.com/"  # Replace with the target URL
all_links = set()
visit_site_links = set()
# 待遍历资源
queue = deque()
def get_all_links(url):
    # Send a GET request
    response = requests.get(url, timeout=10)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all links
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])  # Handle relative links
            parsed_url = urlparse(full_url)
            netloc = parsed_url.netloc
            full_url = urlunparse(parsed_url._replace(query='', fragment='')).lower()
            all_links.add(full_url)
            if netloc == urlparse(website_url).netloc and \
                full_url not in visit_site_links and \
                    not re.match(r'https?://[^\s]+?\.(jpg|jpeg|png|gif|bmp|svg|mp4|exe|mkv)$', full_url):
                queue.append(full_url)
    else:
        print(f"Unable to access the URL: {url}")

def handler(signum, frame):
    print(signum)
    for link in all_links:
        print(link)
    # 在这里执行任何需要的清理操作
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    queue.append(website_url)
    while(len(queue) > 0):
        url = queue.popleft()
        visit_site_links.add(url)
        get_all_links(url)
        print(len(all_links), len(queue))
    print("Found links:")
    for link in all_links:
        print(link)
    