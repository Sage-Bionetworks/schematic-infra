import logging
import pytest
import time
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os

@pytest.fixture(scope="session")
def get_token():
    # try using synapse access token
    if "SYNAPSE_ACCESS_TOKEN" in os.environ:
        token=os.environ["SYNAPSE_ACCESS_TOKEN"]
    elif "TOKEN" in os.environ:
        token = os.environ["TOKEN"]
    else: 
        logger.debug('TOKEN is missing. Please add synapse access token')
    yield token

@pytest.fixture(scope="session")
def example_data_model():
    yield "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"

@pytest.fixture(scope="session")
def HTAN_data_model():
    yield "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"


def fetch(url: str, params: dict):
    return requests.get(url, params=params)

@pytest.fixture(scope="session")
def fetch_request():
    return fetch
