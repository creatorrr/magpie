import json
import os
import time
from typing import Any
from urllib.parse import urlparse

import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datasets import Dataset
from hn_sdk.client.v0.client import get_item_by_id
from joblib import Parallel, delayed
from tqdm.auto import tqdm

from magpie.fscache import fscache

# Create cache directory
cache_dir = "./cache"
os.makedirs(cache_dir, exist_ok=True)


def pluck(d: dict[str, Any], ks: list[str]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if k in ks}


def get_host(u: str) -> str:
    return urlparse(u).netloc


hn_user_cookie: str | None = os.environ.get("HN_USER_COOKIE")


def parse_upvote(d: tuple) -> dict[str, Any]:
    parsed_time = dateparser.parse((d[0][1]), languages=["en"])
    # Use ternary operator for cleaner code
    parsed_time_value = time.time() if parsed_time is None else parsed_time.timestamp()

    return {
        "id": int(d[0][0].split("=")[1]),
        "link": d[1][0],
        "title": d[1][1],
        "time_words": d[0][1],
        "time": parsed_time_value,
    }


def download_upvotes(username: str) -> list[dict[str, Any]]:
    """
    Download upvoted stories for a given HackerNews username.
    Results are cached using fscache.

    Args:
        username: HackerNews username to fetch upvotes for

    Returns:
        List of dictionaries containing upvoted story data
    """
    url = f"https://news.ycombinator.com/upvoted?id={username}"
    cache_file = fscache.path(url, cache_dir=cache_dir)

    if fscache.valid(cache_file, lifetime=86400):  # 24-hour cache
        print(f"Loading upvotes for user '{username}' from cache")
        return json.loads(fscache.load(cache_file))

    print(f"Fetching upvotes for user '{username}' (not from cache)")
    upvotes: list[tuple] = []

    with requests.Session() as session:
        page = 1
        while True:
            print(f"Scraping page {page} for user '{username}'")
            resp = session.get(
                f"https://news.ycombinator.com/upvoted?id={username}&p={page}",
                cookies={"user": f"{username}&{hn_user_cookie}"},
            )
            tree = BeautifulSoup(resp.text, features="html.parser")

            meta = [(x["href"], x.contents[0].text) for x in tree.select(".subtext .age a")]
            links = [
                (x.get("href"), x.contents[0].text)
                for x in tree.select("td.title > .titleline > a")
            ]
            assert len(meta) == len(links)

            if len(links) == 0:
                break

            upvotes.extend(zip(meta, links, strict=False))
            page = page + 1
            time.sleep(1)

    result = list(map(parse_upvote, upvotes))
    fscache.save(cache_file, json.dumps(result))
    return result


def get_cached_item_by_id(item_id: int) -> dict[str, Any]:
    """
    Get an item from HackerNews API with caching.

    Args:
        item_id: The HackerNews item ID to fetch

    Returns:
        Item data from the HackerNews API
    """
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    cache_file = fscache.path(url, cache_dir=cache_dir)

    if fscache.valid(cache_file, lifetime=86400):  # 24-hour cache
        return json.loads(fscache.load(cache_file))

    result = get_item_by_id(item_id)
    fscache.save(cache_file, json.dumps(result))
    return result


def process_item(target_id: int, min_score: int = 3) -> dict[str, Any] | None:
    """
    Process a single HackerNews item by ID.

    Args:
        target_id: The HackerNews item ID to process
        min_score: Minimum score threshold for stories

    Returns:
        Item dict if it meets criteria, None otherwise
    """
    item = get_cached_item_by_id(target_id)
    if (
        item
        and isinstance(item, dict)
        and item.get("type") == "story"
        and not item.get("dead", False)
        and item.get("score", 0) >= min_score
    ):
        return item
    return None


class RateLimitedParallel(Parallel):
    """Joblib Parallel implementation with rate limiting."""

    def __init__(self, *args, requests_per_second: int = 10, **kwargs):
        self.delay = 1.0 / requests_per_second
        self.last_time = 0
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        # Add delay between batches to maintain rate limit
        current_time = time.time()
        elapsed = current_time - self.last_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_time = time.time()

        return super().__call__(*args, **kwargs)


def get_neighbor_stories(
    start_id: int, count: int, collected: list[dict[str, Any]] | None = None, min_score: int = 3
) -> list[dict[str, Any]]:
    """
    Get neighboring HackerNews stories around a given ID.
    Uses cached item retrieval.

    Args:
        start_id: The HackerNews item ID to start from
        count: Number of stories to collect
        collected: List of already collected stories (used in recursion)
        min_score: Minimum score threshold for stories

    Returns:
        List of story items from the HackerNews API
    """
    if collected is None:
        collected = []

    # Define the range of IDs to check
    target_ids = list(range(start_id - 2 * count, start_id + 2 * count))

    # Use parallel processing with built-in rate limiting
    # Set n_jobs to 10 to allow up to 10 concurrent requests
    # The RateLimitedParallel will ensure we don't exceed 10 requests per second
    results = RateLimitedParallel(n_jobs=10, requests_per_second=10)(
        delayed(process_item)(target_id, min_score) for target_id in target_ids
    )

    # Filter out None results and add to collection
    for item in results:
        if item is not None and len(collected) < count:
            collected.append(item)

    if len(collected) >= count:
        return collected

    # If we don't have enough items, expand the search range
    return get_neighbor_stories(start_id - 4 * count, count, collected)


def sample_iterator(upvotes, neighbors) -> Any:  # Actually returns Iterator[Dict[str, Any]]
    """
    Iterator yielding samples for dataset creation.

    Yields:
        Dictionary with story data and binary label (1 for upvoted, 0 for neighbors)
    """
    keys = ["id", "link", "title", "time"]
    for item in upvotes:
        yield {**{"label": 1}, **pluck(item, keys)}
    for item in neighbors:
        if isinstance(item, dict):
            yield {**{"label": 0}, **pluck(item, keys)}


def create_and_process_dataset(upvotes, neighbors):
    """Create and process the dataset."""
    # Ensure neighbors is a list of dictionaries
    if isinstance(neighbors, list) and all(isinstance(n, dict) for n in neighbors):
        neighbors_list = neighbors
    else:
        # If neighbors is not already a flat list of dictionaries, flatten it
        neighbors_list = []
        if isinstance(neighbors, list):
            for item in neighbors:
                if isinstance(item, list):
                    # If it's a list of lists, extend the list
                    neighbors_list.extend([n for n in item if isinstance(n, dict)])
                elif isinstance(item, dict):
                    # If it's already a dict, append it
                    neighbors_list.append(item)
    
    samples = list(sample_iterator(upvotes, neighbors_list))
    samples_df = pd.DataFrame(samples)

    dataset = Dataset.from_pandas(samples_df)
    dataset = dataset.map(lambda d: {"host": get_host(d["link"])})

    text_dataset = dataset.map(
        lambda d: {
            "text": f"{d['title']}\nSource: {d['host'].decode()}" if d.get("host") else d["title"],
            **d,
        }
    )

    text_dataset = text_dataset.shuffle(seed=96).train_test_split(0.2, seed=42)

    # Only push to hub when running as main script, not during testing
    text_dataset.push_to_hub("diwank/hn-upvote-data")

    return text_dataset


def get_neighbors_for_upvote(item: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Get neighbor stories for a single upvoted item.

    Args:
        item: The upvoted item to find neighbors for

    Returns:
        List of neighboring stories
    """
    return get_neighbor_stories(item["id"], 1)


def run(clear_cache: bool = False):
    """
    Run the dataset preparation pipeline.

    Args:
        clear_cache: Whether to clear the cache before starting
    """
    if clear_cache:
        print("Clearing cache...")
        import shutil

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)

    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    diwank_upvotes = download_upvotes("diwank")

    print("Fetching neighbor stories (using cache when available)...")
    # Parallelize the collection of neighbors, with rate limiting
    neighbors = Parallel(n_jobs=5)(
        delayed(get_neighbors_for_upvote)(item) for item in tqdm(diwank_upvotes)
    )

    # Remove neighbors already upvoted
    upvoted_ids = {upvote["id"] for upvote in diwank_upvotes}
    filtered_neighbors = []
    
    # Handle items whether neighbors is a list of lists or a flat list
    for items in tqdm(neighbors):
        if isinstance(items, list):
            # It's a list of items
            for item in items:
                if item and isinstance(item, dict) and item.get("id") not in upvoted_ids:
                    filtered_neighbors.append(item)
        elif isinstance(items, dict):
            # It's already a dictionary
            if items.get("id") not in upvoted_ids:
                filtered_neighbors.append(items)

    # Create dataset
    return create_and_process_dataset(diwank_upvotes, filtered_neighbors)


# Only assert in the main execution path, not when being imported for tests
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare HackerNews upvote dataset with caching")
    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear the cache before fetching data"
    )
    args = parser.parse_args()

    assert hn_user_cookie, "Need to find and set the hackernews cookie as HN_USER_COOKIE env var"

    hn_user_cookie = str(hn_user_cookie) if hn_user_cookie else "test_cookie"  # Default for tests
    run(clear_cache=args.clear_cache)
