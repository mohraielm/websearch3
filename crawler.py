# crawler.py mohraiel
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.request import urlopen
from urllib.parse import urljoin


def get_html(url):
    response = urlopen(url)
    content_type = response.headers.get("Content-Type", "")
    # if its html or shtml decode and read content
    if "html" in content_type:
        return response.read().decode("utf-8")
    return None


def extract_links(base_url, html):
    sp = BeautifulSoup(html, "html.parser")
    links = []
    # to find all anchor tags
    for tag in sp.find_all("a", href=True):
        href = tag["href"]
        full = urljoin(base_url, href)
        if full.startswith("https://www.cpp.edu/") and (
            full.endswith(".html")
            or full.endswith(
                ".shtml"
            )  # added shtml since most of the pages in cppedu had it
        ):
            links.append(full)
    return links


def store_page(collection, url, html, is_target):
    collection.update_one(
        {"_id": url},
        {"$set": {"url": url, "html": html, "target": is_target}},
        upsert=True,
    )


def main():
    # connecting mongo
    client = MongoClient("localhost", 27017)
    db = client["WebSearch3"]
    pages_collection = db["pages"]

    frontier = ["https://www.cpp.edu/sci/computer-science/"]
    visited = set()

    # frontier crawling loop
    while frontier:
        current_url = frontier.pop(0)  # getting next url
        if current_url in visited:
            continue
        visited.add(current_url)
        print(f"Visiting: {current_url}")  # just to make sure the target html is right

        html = get_html(current_url)
        if not html:
            continue

        # Cmy target html
        sp = BeautifulSoup(html, "html.parser")
        if sp.find("h1", {"class": "cpp-h1"}, string="Permanent Faculty"):
            print("Target page found!")
            store_page(pages_collection, current_url, html, is_target=True)
            break
        store_page(pages_collection, current_url, html, is_target=False)
        # add new links to frontier
        links = extract_links(current_url, html)
        for link in links:
            if link not in visited:
                frontier.append(link)


if __name__ == "__main__":
    main()
