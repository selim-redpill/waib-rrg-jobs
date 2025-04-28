"""
Main entrypoint for the RRG WAIB Scheduler.

This script connects to MongoDB, fetches **all** pages of vehicle stock data
from the Renault Retail Group API, and upserts both individual car records
and aggregated statistics into MongoDB collections.
"""

import os
from typing import Any, Dict, List, Optional

from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from pymongo import UpdateOne
from pymongo.mongo_client import MongoClient as PyMongoClient
from models import CarStockResponse, CarStockItem, Aggregations

from logger import logger

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

RRG_API_URL = "https://api.retail-renault-group.fr/car_stocks"

def connect_to_mongo() -> PyMongoClient:
    """
    Establish a connection to the MongoDB cluster.

    Reads the MONGO_URI from environment variables, attempts to connect,
    and returns a PyMongoClient instance.

    Raises:
        EnvironmentError: If MONGO_URI is not set.
    """
    if not MONGO_URI:
        raise EnvironmentError("Missing MONGO_URI")

    client: PyMongoClient = PyMongoClient(MONGO_URI)
    logger.info("✅ Connected to MongoDB")
    return client


def fetch_rrg_stocks() -> CarStockResponse:
    """
    Fetch and parse **all pages** of vehicle stock data from the RRG API.

    Follows the `hydra:next` link in each page until exhausted, aggregates
    every CarStockItem, and returns a single CarStockResponse with:
      - totalItems: the grand total from the first page
      - items:       the flattened list of every CarStockItem
      - aggregations: the parsed Aggregations model
    """
    all_items: List[CarStockItem] = []
    aggregations_raw: Dict[str, Any] = {}
    total_items: int = 0

    next_url: Optional[str] = RRG_API_URL
    page: int = 1
    params: Optional[Dict[str, int]] = {"itemsPerPage": 500, "page": page}

    while next_url:
        logger.info("📦 Fetching page %d from %s", page, next_url)
        resp = requests.get(next_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if total_items == 0:
            total_items = data["hydra:totalItems"]

        members = data.get("hydra:member", [])
        logger.info("↳ Retrieved %d items on page %d", len(members), page)
        all_items.extend(CarStockItem(**raw) for raw in members)

        # stash the raw aggregations (same on every page)
        aggregations_raw = data["aggregations"]

        # prepare next iteration
        view = data.get("hydra:view", {})
        next_link = view.get("hydra:next")
        if next_link:
            next_url = urljoin(RRG_API_URL, next_link)
            page += 1
            params = None  # subsequent calls embed page in next_url
        else:
            next_url = None

    logger.info("✅ Completed fetching %d vehicles across %d pages", len(all_items), page)

    # parse the raw dict into our Aggregations Pydantic model
    aggs: Aggregations = Aggregations.model_validate(aggregations_raw)

    return CarStockResponse(
        totalItems=total_items,
        items=all_items,
        aggregations=aggs
    )

def main() -> None:
    """
    Main scheduler workflow.

    1. Connects to MongoDB.
    2. Fetches **all** vehicle stock data (all pages).
    3. Bulk-upserts each CarStockItem into "vehicle_stocks".
    4. Replaces the "latest" document in "vehicle_stock_aggregations".
    5. Closes the MongoDB connection.
    """
    logger.info("🚀 Starting scheduler")
    client = connect_to_mongo()
    db = client["waib_rrg_db"]
    stocks = db["vehicle_stocks"]
    aggs_col = db["vehicle_stock_aggregations"]

    # 1) fetch & parse all pages
    stock_data = fetch_rrg_stocks()

    # 2) upsert vehicles in bulk
    ops = [
        UpdateOne({"id": item.id}, {"$set": item.model_dump()}, upsert=True)
        for item in stock_data.items
    ]
    if ops:
        result = stocks.bulk_write(ops)
        logger.info(
            "Upserted %d records (inserts=%d / updates=%d)",
            result.upserted_count + result.modified_count,
            result.upserted_count,
            result.modified_count,
        )

    # 3) store aggregations (replace the “latest”)
    aggs_doc = stock_data.aggregations.model_dump()
    aggs_doc["timestamp"] = stock_data.items[0].dateOfEntryIntoStock
    aggs_col.replace_one({"_id": "latest"}, aggs_doc, upsert=True)
    logger.info("✅ Aggregations updated")

    client.close()
    logger.info("🏁 Scheduler run complete")


if __name__ == "__main__":
    main()
