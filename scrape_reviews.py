import json
import os
from pathlib import Path
import requests
import time

from bs4 import BeautifulSoup
from bs4.element import Tag
import click
import pandas as pd
import structlog

logger = structlog.get_logger()


def extract_div_text(review_div, div_class_name: str) -> str:
    """Helper function to get contents of div if there are any."""
    if review_text_raw_html := review_div.find("div", {"class": div_class_name}):
        return review_text_raw_html.text.strip()
    return ""


def extract_review_data(review_div: Tag) -> dict:
    """Extracts reviewer name, count of their reviews, their country, given stars and review itself."""
    reviewer_name = extract_div_text(
        review_div, "consumer-information__name"
    )  # review_div.find("div", {"class": "consumer-information__name"}).text.strip()
    reviewer_review_count = extract_div_text(
        review_div, "consumer-information__review-count"
    )  # review_div.find("div", {"class": "consumer-information__review-count"}).text.strip()
    reviewer_country = extract_div_text(
        review_div, "consumer-information__location"
    )  # review_div.find("div", {"class": "consumer-information__location"}).text.strip()
    review_date = json.loads(
        review_div.find("div", {"class": "review-content-header__dates"}).script.contents[0].strip()
    )
    stars_given = review_div.find("div", {"class": "star-rating star-rating--medium"}).img.get("alt")
    review_title = review_div.find("h2", {"class": "review-content__title"}).text.strip()
    # review text can be separated into paragraphs and those are separated only by </br> tag in underlying HTML
    # which, when getting the 'text' attribute of the element, would lead to paragraphs which doesn't have spaces
    # between them (which could possibly cause problems in further stage of analysis - part of speech tags etc.)
    if review_text_raw_html := review_div.find("p", {"review-content__text"}):
        review_text = " ".join(review_text_raw_html.stripped_strings)
    else:
        review_text = ""

    return {
        "reviewer_name": reviewer_name,
        "reviewer_country": reviewer_country,
        "reviewer_review_count": reviewer_review_count,
        "review_date": review_date,
        "stars_given": stars_given,
        "review_title": review_title,
        "review_text": review_text,
    }


def process_reviews_soup(reviews_soup: Tag) -> list:
    """Process one page of review data from Trustpilot."""
    review_data = []
    review_cards = reviews_soup.findAll("div", {"class": "review-card"})
    for review_card in review_cards:
        # it may happen that review was violating Trustpilot conditions, in which case it's all blank
        # and there's a banner informing about violation - skip those as there's no information there
        if not review_card.find("div", {"class": "review-report-banner"}):
            review_data.append(extract_review_data(review_card))

    return review_data


@click.command()
@click.option("--url_pattern", prompt="Url of the first page of company reviews")
@click.option("--number_of_pages", prompt="Number of pages to scrape", type=int)
@click.option("--path", prompt="Path where to store the result (csv)")
def scrape_reviews(url_pattern: str, number_of_pages: int, path: str):
    """Scrape reviews of given firm (specified by URL of first page of reviews)
    from Trustpilot.
    :param url: url of the first page of reviews of chosen company on Trustpilot
    :param number_of_pages: number of pages of reviews to scrape
    :param filename: path where to store results (csv file)
    """
    headers = {"user_agent": "https://github.com/jakubpernis/review_wordcloud"}
    review_data = []

    with requests.Session() as session:
        for i in range(number_of_pages):
            url = f"{url_pattern}?page={i + 1}"
            try:
                resp = session.get(url, headers=headers, timeout=30)
            except Exception as e:
                logger.info("Get request failed...", url=url, exception=str(e))
                continue

            reviews_soup = BeautifulSoup(resp.text, features="lxml")
            review_data.extend(process_reviews_soup(reviews_soup))

            # crawl delay in robots.txt is set to 10
            time.sleep(10)

    reviews_df = pd.DataFrame(review_data)

    # create directories in path if there are some and don't exist
    if parent_dirs := os.path.dirname(path):
        Path(parent_dirs).mkdir(parents=True, exist_ok=True)

    reviews_df.to_csv(path, index=False)


if __name__ == "__main__":
    scrape_reviews()
