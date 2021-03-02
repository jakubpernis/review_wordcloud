# Trustpilot reviews wordcloud

Small utility for quick glance on what the Trustpilot reviews of some company are about.

Firstly, you need to scrape those reviews from the Trustpilot website (unless you are willing to pay for their business API). After running `python scrape_reviews.py` you will be prompted about which company's reviews would you like to check (specified by a url of that company on [Trustpilot](https://www.trustpilot.com/)), how many pages of reviews you want to scrape and where to save the data.

Below is an example which I used to get the data which are then used in `wordcloud.ipynb` Jupyter notebook.
```
python scrape_reviews.py

Url of the first page of company reviews: https://www.trustpilot.com/review/kiwi.com
Number of pages to scrape: 500
Path where to store the result (csv): data/reviews.csv
```

In stored data there's a column `review_text` (among others) which contains the raw text of the reviews. Wordcloud can be constructed directly from the raw text, it's nicely described in [this tutorial on Datacamp](https://www.datacamp.com/community/tutorials/wordcloud-python). However, there's also an option to construct wordcloud using tokens frequencies, which is the approach we chose to use because we can preprocess the raw text more flexibly and in any way we want. For that purpose we defined custom `TextProcessor` class.

Requires Python >= 3.8.