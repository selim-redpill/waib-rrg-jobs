# WAIB-RRG-Jobs

A Python service designed to automate the daily retrieval of vehicle stock data from the Renault Retail Group API, storing it in a MongoDB database for use by the WAIB project.

## Overview

This service connects to the Renault Retail Group API, fetches all pages of vehicle stock data, and efficiently upserts each car record into MongoDB. The system handles pagination automatically and provides detailed logging with color-coded console output.

## Features

- **Complete Data Retrieval**: Fetches all pages of vehicle inventory data from RRG API
- **Efficient Database Operations**: Uses bulk upsert operations for optimal performance
- **Stale Record Management**: Automatically removes records that no longer exist in the source API
- **Colorized Logging**: Custom logger with color-coded output based on log severity levels
- **Containerized Deployment**: Ready-to-use Docker configuration

## Technologies Used

- Python 3.10+
- Poetry for dependency management
- MongoDB for data storage
- Pydantic for data validation and modeling
- Docker for containerization

## Installation

### Prerequisites

- Python 3.10 or higher
- MongoDB database (connection string required)
- Poetry 1.8.5 or higher

### Setup

1. Clone this repository
2. Install dependencies with Poetry:

```bash
poetry install
```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
MONGO_URI=mongodb+srv://username:password@your-cluster.mongodb.net/
```

## Usage

### Running Locally

```bash
poetry run python main.py
```

### Running with Docker

Build the Docker image:

```bash
docker build -t waib-rrg-jobs .
```

Run the container with environment variables:

```bash
docker run -e MONGO_URI="mongodb+srv://username:password@your-cluster.mongodb.net/" waib-rrg-jobs
```

## Project Structure

- `main.py` - Main entry point and workflow orchestration
- `models.py` - Pydantic models for RRG API response data
- `logger.py` - Custom logger configuration with color formatting
- `Dockerfile` - Container configuration
- `pyproject.toml` - Project metadata and dependencies

## Data Model

The service processes vehicle stock data with the following key attributes:

- Vehicle identification information
- Pricing and availability
- Technical specifications
- Location and inventory data

For a complete schema, refer to the `CarStockItem` model in `models.py`.

## Deployment

The service is designed to be deployed as a scheduled job (e.g., using cron, Kubernetes CronJob, or a similar scheduler) to ensure regular data updates.

## Author

Selim Alastra <selim.alastra@redpill.paris>
