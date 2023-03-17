import os
import logging
import pytest
import requests
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def csv_export(description, dt_string, CONCURRENT_REQUEST, total_error_num, total_504_num, time_diff):
    fields={"Description": description, "Date time": dt_string, "Number of Concurrent Requests": CONCURRENT_REQUEST, "Number of error": total_error_num, "total 504 error":total_504_num, "Latency": time_diff}
    df = pd.DataFrame(fields, index=[0])
    df.to_csv("latency.csv", mode='a', index=False, header=False)

@pytest.fixture(scope="session")
def fetch_request():
    return fetch

@pytest.fixture(scope="session")
def output_to_csv():
    return csv_export
