"""
Main entrypoint for the RRG WAIB Scheduler.

This script connects to MongoDB, fetches **all** pages of vehicle stock data
from the Renault Retail Group API, and upserts each individual car record
into MongoDB.
"""

import os
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from pymongo import UpdateOne
from pymongo.mongo_client import MongoClient as PyMongoClient

from models import CarStockItem
from logger import logger

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

RRG_API_URL = "https://api.retail-renault-group.fr/car_stocks"

def connect_to_mongo() -> PyMongoClient:
    """
    Establish a connection to the MongoDB cluster.

    Raises:
        EnvironmentError: If MONGO_URI is not set.

    Returns:
        PyMongoClient: Connected MongoClient instance.
    """
    if not MONGO_URI:
        raise EnvironmentError("Missing MONGO_URI")
    client: PyMongoClient = PyMongoClient(MONGO_URI)
    logger.info("✅ Connected to MongoDB")
    return client


def fetch_rrg_stocks() -> List[CarStockItem]:
    """
    Fetch and parse **all pages** of vehicle stock data from the RRG API.

    Follows pagination and returns a flat list of CarStockItem objects.

    Returns:
        List[CarStockItem]: List of all fetched car stock items.
    """
    all_items: List[CarStockItem] = []
    next_url: Optional[str] = RRG_API_URL
    page: int = 1
    params: Optional[Dict[str, int]] = {"itemsPerPage": 500, "page": page}

    while next_url:
        logger.info("📦 Fetching page %d from %s", page, next_url)
        resp = requests.get(next_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        members = data.get("hydra:member", [])
        logger.info("↳ Retrieved %d items on page %d", len(members), page)
        all_items.extend(CarStockItem(**raw) for raw in members)

        # Prepare next iteration
        view = data.get("hydra:view", {})
        next_link = view.get("hydra:next")
        if next_link:
            next_url = urljoin(RRG_API_URL, next_link)
            page += 1
            params = None  # subsequent calls embed page in next_url
        else:
            next_url = None

    logger.info("✅ Completed fetching %d vehicles across %d pages", len(all_items), page)
    return all_items


def main() -> None:
    """
    Main scheduler workflow.

    1. Connects to MongoDB.
    2. Fetches **all** vehicle stock data (all pages).
    3. Bulk-upserts each CarStockItem into "vehicle_stocks".
    4. Deletes entries that no longer exist.
    5. Closes the MongoDB connection.
    """
    logger.info("🚀 Starting scheduler")
    client = connect_to_mongo()
    db = client["waib_rrg_db"]
    stocks = db["vehicle_stocks"]

    # 1) fetch & parse all pages
    stock_items = fetch_rrg_stocks()
    current_ids = {item.id for item in stock_items}

    # 2) upsert vehicles in bulk
    ops = [
        UpdateOne({"id": item.id}, {"$set": item.model_dump()}, upsert=True)
        for item in stock_items
    ]
    if ops:
        result = stocks.bulk_write(ops)
        logger.info(
            "Upserted %d records (inserts=%d / updates=%d)",
            result.upserted_count + result.modified_count,
            result.upserted_count,
            result.modified_count,
        )

    # 3) delete vehicles that no longer exist
    existing_ids = set(
        doc["id"] for doc in stocks.find({}, {"id": 1})
    )
    to_delete_ids = list(existing_ids - current_ids)

    if to_delete_ids:
        delete_result = stocks.delete_many({"id": {"$in": to_delete_ids}})
        logger.info("Deleted %d stale records", delete_result.deleted_count)
    else:
        logger.info("🧼 No stale records to delete")

    client.close()
    logger.info("🏁 Scheduler run complete")


if __name__ == "__main__":
    main()