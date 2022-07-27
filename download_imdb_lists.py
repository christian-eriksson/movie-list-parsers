#!/usr/bin/env python
from multiprocessing import Pool
import os
import sys
import requests

from playwright.sync_api import sync_playwright


def find_lists(keywords: str, max_list_count: int):
    list_urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        browser.contexts.clear()
        page = browser.new_page()
        page.goto("http://duckduckgo.com")
        page.locator("#search_form_input_homepage").fill(
            f"{keywords} site:imdb.com/list"
        )
        page.locator("#search_button_homepage").click()
        page.wait_for_load_state("networkidle")
        result = page.locator("#links")
        counter = 1
        while (
            result.locator("div.nrn-react-div").count() < max_list_count
            and counter <= 10
        ):
            page.locator(f"#rld-{counter}").click()
            page.wait_for_timeout(2000)
            page.wait_for_load_state("domcontentloaded")
            counter += 1

        list_urls = result.locator("div.nrn-react-div h2 a").evaluate_all(
            "(links) => links.reduce((urls, link) => {urls.push(link.href); return urls}, [])"
        )

        browser.close()

        return list_urls[0:max_list_count]


def url_response(url_item):
    path, url = url_item
    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url, stream=True)
    with open(path, "wb") as file:
        for chunk in response:
            file.write(chunk)


if __name__ == "__main__":
    try:
        keywords = sys.argv[1]
    except:
        print("ERROR: provide some key words to search for in arg 1", file=sys.stderr)
        exit(1)

    try:
        dir_path = sys.argv[2]
    except:
        dir_path = "/tmp"

    try:
        max_list_count = int(sys.argv[3])
    except:
        max_list_count = 10

    list_urls = find_lists(keywords, max_list_count)
    list_url_items = [
        (
            f"{dir_path}/{keywords.replace(' ', '_')}_{index}.csv",
            f"{list_urls[index].strip('/')}/export?ref_=ttls_otexp",
        )
        for index in range(len(list_urls))
    ]

    with Pool(os.cpu_count()) as p:
        p.map(url_response, list_url_items)
