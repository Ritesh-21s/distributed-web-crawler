import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from collections import deque

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

links_count = {}

os.makedirs("pages", exist_ok=True)

def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.Timeout:
        print("Timeout:", url)

    except requests.exceptions.ConnectionError:
        print("Connection error:", url)

    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e.response.status_code, url)

    except requests.exceptions.RequestException as e:
        print("Other request error:", e)
        
    return None


def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("#"):
            continue
        if href.startswith(("mailto:", "javascript:", "tel:")):
            continue

        full_url = urljoin(base_url, href)
        links.add(full_url)

    return links

def url_to_filename(url):
    parsed = urlparse(url)

    path = parsed.path.rstrip("/")

    last_part = path.split("/")[-1]

    if not last_part:
        last_part = "index"

    return last_part + ".html"

def crawl(seed_url, max_pages=5):
    queue = deque([seed_url])
    visited = set()

    while queue and len(visited) < max_pages:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        print(f"Crawling: {current_url}")

        html = fetch_page(current_url)
        if html is None:
            continue

        visited.add(current_url)

        with open(os.path.join("pages", url_to_filename(current_url)), "w", encoding="utf-8") as f:
            f.write(html)

        links = extract_links(html, current_url)

        links_count[current_url] = len(links)

        for link in links:
            if link not in visited:
                queue.append(link)

    return visited

seed = "https://en.wikipedia.org/wiki/Michael_Jackson"
visited_pages = crawl(seed, max_pages=10)

print("\nCrawled Pages:")

for page in visited_pages:
    print(page , links_count[page])
