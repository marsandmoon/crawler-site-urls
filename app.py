import argparse
import signal
import sys
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import urllib3
from collections import deque

# 忽略所有 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
website_url = "https://mingdao.com/"  # Replace with the target URL
timeout = 10
ssl_verify = False

# Output
all_links = set()
visit_site_links = set()
all_imgs = set()

# 待遍历资源
queue = deque()
def get_all_links(url):
    # Send a GET request
    response = requests.get(url, timeout=timeout, verify=ssl_verify)
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
        # Find all imags
        for img in soup.find_all('img', src=True):
            all_imgs.add(urljoin(website_url, img['src']))
    else:
        print(f"Unable to access the URL: {url}")

def print_result():
    samesite = set()
    othersite = set()
    for link in all_links:
        if urlparse(link).hostname == urlparse(website_url).hostname:
            samesite.add(link)
        else:
            othersite.add(link)
    print('\nsame site:')
    for link in sorted(samesite):
        print(link)
    print('\nother site:')
    for link in sorted(othersite):
        print(link)
    print('\nimgs:')
    for link in sorted(all_imgs):
        print(link)

def handler(signum, frame):
    print(signum)
    print_result()
    # 在这里执行任何需要的清理操作
    sys.exit(0)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='crawler site')
    arg_parser.add_argument('--url', type=str, help='the target site: https://example.com')
    arg_parser.add_argument('--timeout', type=int, help='timeout seconds of each request')
    args = arg_parser.parse_args()
    if args.url:
        website_url = args.url
    if args.timeout:
        timeout = args.timeout
    signal.signal(signal.SIGINT, handler)
    queue.append(website_url)
    while(len(queue) > 0):
        url = queue.popleft()
        visit_site_links.add(url)
        get_all_links(url)
        print(len(all_links), len(queue))
    print("Found links:")
    print_result()
    