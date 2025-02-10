# coding: utf-8
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from datasets import Dataset
import dateparser
from hn_sdk.client.v0.client import get_item_by_id
import pandas as pd
import requests
from tqdm.auto import tqdm

pluck = lambda d, ks: {k: v for k, v in d.items() if k in ks}
get_host = lambda u: urlparse(u).netloc

hn_user_cookie: str = os.environ.get("HN_USER_COOKIE")
assert hn_user_cookie, "Need to find and set the hackernews cookie as HN_USER_COOKIE env var"

def download_upvotes(username: str):
    upvotes = []
    parse = lambda d: dict(
        id=int(d[0][0].split('=')[1]),
        link=d[1][0],
        title=d[1][1],
        time_words=d[0][1],
        time=dateparser.parse((d[0][1]), languages=["en"]).timestamp(),
    )

    with requests.Session() as session:
        page = 1
        while True:
            print(f"Scraping page {page} for user '{username}'")
            resp = session.get(
                f"https://news.ycombinator.com/upvoted?id={username}&p={page}",
                cookies={"user": f"{username}&{hn_user_cookie}"},
            )
            tree = BeautifulSoup(resp.text)

            meta = [(x["href"], x.contents[0].text) for x in tree.select(".subtext .age a")]
            links = [(x.get("href"), x.contents[0].text) for x in tree.select("td.title > .titleline > a")]
            assert len(meta) == len(links)

            if len(links) == 0:
                break

            upvotes.extend(zip(meta, links))
            page = page + 1
            time.sleep(1)

    return list(map(parse, upvotes))

diwank_upvotes = download_upvotes("diwank")

def get_neighbor_stories(start_id, count, collected=[], min_score=3):
    for target_id in range(start_id - 2*count, start_id + 2*count):
        if len(collected) >= count:
            break
        time.sleep(0.1)
        item = get_item_by_id(target_id)
        if item["type"] == "story" and not item.get("dead", False) and item["score"] >= min_score:
            collected.append(item)
    if len(collected) >= count:
        return collected
    else:
        return get_neighbor_stories(start_id - 4*count, count, collected)

neighbors = [get_neighbor_stories(item["id"], 3) for item in tqdm(diwank_upvotes)]

def sample_iterator():
    keys = ["id", "link", "title", "time"]
    for item in diwank_upvotes:
        yield {**{"label": 1}, **pluck(item, keys)}
    for itemlist in neighbors:
        for item in itemlist:
            yield {**{"label": 0}, **pluck(item, keys)}

samples = list(sample_iterator())
samples_df = pd.DataFrame(samples)

dataset = Dataset.from_pandas(samples_df)
dataset = dataset.map(lambda d: {"host": get_host(d["link"])})

text_dataset = dataset.map(lambda d: {"text": f'{d["title"]}\nSource: {d["host"].decode()}' if d.get("host") else d["title"]})
text_dataset = text_dataset.shuffle(seed=96).train_test_split(0.3, seed=42)
text_dataset.push_to_hub("diwank/hn-upvote-data")
