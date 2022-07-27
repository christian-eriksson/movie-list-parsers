#!/usr/bin/env python3

import re
import sys
import requests

from datetime import datetime
from html.parser import HTMLParser
from typing import List, Optional, Tuple


class WrongPageDateException(Exception):
    pass


def get_href_value(attrs: List[Tuple[str, str]]) -> str:
    href_value = ""
    for attr in attrs:
        if attr[0] == "href":
            href_value = attr[1]
            break
    return href_value


class ParseInfo250(HTMLParser):
    def __init__(self, year: int, month: int, day: Optional[int] = None):
        super().__init__()
        self.titles = []
        self.year = year
        self.month = month
        self.day = day

        self.searching_td = False
        self.searching_movie_link = False
        self.searching_date_link = False
        self.searching_span = False
        self.movie_id = ""
        self.next_date_candidate = ""
        self.next_date = None

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.searching_td = True

        date_href_pattern = re.compile(r"/charts/\?(\d{4}/\d{2}/\d{2})")
        movie_href_pattern = re.compile(r"/movie/\?(\w+)")
        href_value = get_href_value(attrs)
        movie_href_match = movie_href_pattern.match(href_value)
        date_href_match = date_href_pattern.match(href_value)
        if tag == "a":
            if movie_href_match:
                self.movie_id = movie_href_match.group(1)
                self.searching_movie_link = True
            if date_href_match:
                self.next_date_candidate = date_href_match.group(1)
                self.searching_date_link = True
        if tag == "span":
            self.searching_span = True

    def handle_endtag(self, tag):
        if tag == "td":
            self.searching_td = False
        if tag == "a":
            self.searching_movie_link = False
            self.searching_date_link = False
        if tag == "span":
            self.searching_span = False

    def handle_data(self, data):
        content = str(data).strip()
        if self.searching_td:
            if self.searching_date_link:
                next_page_pattern = re.compile(r"→")
                if next_page_pattern.match(content):
                    date_parts = [
                        int(part) for part in self.next_date_candidate.split("/")
                    ]
                    self.next_date = datetime(
                        date_parts[0], date_parts[1], date_parts[2]
                    )
            if self.searching_movie_link and self.searching_span:
                title_pattern = re.compile(r"(.*)(\([\d]{4}\))")
                title_match = title_pattern.match(content)
                if title_match:
                    title = title_match.groups()[0].strip()
                    if title:
                        date = f"{str(self.year)}-{str(self.month)}-{str(self.day)}"
                        self.titles.append(
                            [
                                f"tt{self.movie_id}",
                                date,
                                date,
                                "",
                                title,
                                f"https://www.imdb.com/title/{self.movie_id}",
                                "movie",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                            ]
                        )


def get_list_page_html(year: int, month: int, day: Optional[int] = None):
    url = "http://top250.info/charts/?"
    url = f"{url}{year}"
    month_string = f"0{month}" if month < 10 else month
    url = f"{url}/{month_string}"
    if day:
        day_string = f"0{day}" if day < 10 else day
        url = f"{url}/{day_string}"

    resp = requests.get(url)
    response = resp.content.decode("utf8")
    clean_html = re.sub(r"[\n\r\t]", "", response)
    return clean_html


try:
    date_pieces = sys.argv[1].split("-")
    year = int(date_pieces[0])
    month = int(date_pieces[1])
    day = int(date_pieces[2])
except:
    print(
        "WARNING: no date or wrong date format provided, should be in the form: 'YYYY-MM-DD'. Will parse from 1996-04-26."
    )
    year = 1996
    month = 4
    day = 26

start_date = datetime(year=year, month=month, day=day)
today = datetime.now()
end_year = today.year
end_month = today.month
end_day = today.day
max_days = (today - start_date).days
date = start_date
date_counter = 0
start_row = 0
while True:
    list_page_html = get_list_page_html(year=date.year, month=date.month, day=date.day)
    parser = ParseInfo250(year=date.year, month=date.month, day=date.day)
    parser.feed(list_page_html)
    titles = parser.titles
    title_count = len(titles)
    if title_count > 0:
        if start_row == 0:
            print(
                "Position,Const,Created,Modified,Description,Title,URL,"
                + "Title Type,IMDb Rating,Runtime (mins),Year,Genres,Num Votes,"
                + "Release Date,Directors"
            )
            start_row += 1
        print(
            *[
                f"{start_row+index}," + ",".join(titles[index])
                for index in range(title_count)
            ],
            sep="\n",
        )
        start_row += title_count
    if not parser.next_date:
        break
    else:
        date = parser.next_date

    date_counter += 1
    if date_counter > max_days:
        break
