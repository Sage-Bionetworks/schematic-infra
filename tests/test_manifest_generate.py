
import logging
import pytest
import requests
import datetime
from datetime import datetime
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import csv
import pandas as pd
# from .general import apiTester

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CONCURRENT_REQUEST = 5
TIME_OUT_LIMIT_GENERATE_NEW_MANIFEST = 30
TIME_OUT_LIMIT_GENERATE_EXISTING_MANIFEST = 60

class TestManifestOperation:
    @pytest.mark.parametrize("output_format", ["google_sheet"])
    @pytest.mark.parametrize("dataset_id", [None, "syn51078367"])
    def test_generate_manifest(self, get_token, example_data_model, fetch_request, output_to_csv, output_format, dataset_id):
        base_url = "https://schematic-dev.api.sagebionetworks.org/v1/manifest/generate"
        input_token = get_token

        params = {
            "schema_url": example_data_model,
            "title": "Example",
            "data_type": ["Patient"],
            "use_annotations": False,
            "input_token": input_token,
            "output_format": output_format,
            "dataset_id": dataset_id
        }

        with ThreadPoolExecutor() as executor:
            total_error_num = 0
            total_504_num = 0
            start_time = time.time()
            # get current date time object
            now = datetime.now()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            # set an empty dictionary to store date time object

            futures = [
                    executor.submit(fetch_request, base_url, params) for x in range(CONCURRENT_REQUEST)
                ]
            for f in concurrent.futures.as_completed(futures):
                try:
                    status_code = f.result().status_code
                    assert status_code == 200
                    if status_code != 200:
                        total_error_num = total_error_num + 1
                        logger.debug("Error code: ", status_code)
                        if status_code == 504:
                            total_504_num = total_504_num + 1
                except Exception as exc:
                    logger.debug(f"generated an exception:{exc}")
            time_diff = round(time.time() - start_time, 2)

            # record latency and errors
            if not params["dataset_id"]:
                if output_format == "google_sheet":
                    description = "Generating a new google sheet using the example data model"
                else:
                    description = "Generating a new excel sheet using the example data model"
            else:
                if output_format == "google_sheet":
                    description = "Generating an existing google sheet using the example data model"
                else:
                    description = "Generating an existing excel sheet using the example data model"

            output_to_csv(description, dt_string, CONCURRENT_REQUEST, total_error_num, total_504_num, time_diff)

            if dataset_id:
                assert time_diff < TIME_OUT_LIMIT_GENERATE_EXISTING_MANIFEST
            else:
                assert time_diff < TIME_OUT_LIMIT_GENERATE_NEW_MANIFEST
