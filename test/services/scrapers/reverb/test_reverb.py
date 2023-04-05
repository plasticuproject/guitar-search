"""test_reverb.py"""

import unittest
import json
from pathlib import Path
from io import StringIO
from typing import List, Dict, Collection, Union
from unittest import mock
from services.scrapers.reverb.reverb import scrape_reverb, dump_scrape
from services.scrapers.reverb.reverb_models import Listing


# pylint: disable=too-few-public-methods
class MockResponse:
    """Mock API responses."""

    def __init__(self,
                 response_data: Union[str, Dict[str, Collection[str]]],
                 status_code: int) -> None:
        self.response_data = response_data
        self.status_code = status_code
        self.text = response_data

    def json(self) -> Union[str, Dict[str, Collection[str]]]:
        """Mock requests.Models.Response.json method"""
        return self.response_data


# pylint: disable=unused-argument
def mocked_requests_get(*args: str, **kwargs: str) -> MockResponse:
    """This method will be used by the mock to replace requests.get."""
    url = "https://api.reverb.com/api/categories/"
    electric_endpoints = [
        f"{url}dfd39027-d134-4353-b9e4-57dc6be791b9",
        f"{url}dfd39027-d134-4353-b9e4-57dc6be791b9?page=1"]
    acoustic_endpoints = [
        f"{url}3ca3eb03-7eac-477d-b253-15ce603d2550",
        f"{url}3ca3eb03-7eac-477d-b253-15ce603d2550?page=1"]
    json_error_1 = f"bad1{url}dfd39027-d134-4353-b9e4-57dc6be791b9"

    error_code = {
        "message": "This is the human readable summary of problems",
        "errors": {"Invalid url": ["Url is invalid."]}
    }

    if args[0] in electric_endpoints:
        with open("./test/services/scrapers/reverb/"
                  "dumps/test_reverb_electric_guitars.json",
                  "r", encoding="utf-8") as infile:
            data = json.loads(infile.read())
        return MockResponse(data, 200)
    if args[0] in acoustic_endpoints:
        with open("./test/services/scrapers/reverb/"
                  "dumps/test_reverb_acoustic_guitars.json",
                  "r", encoding="utf-8") as infile:
            data = json.loads(infile.read())
        return MockResponse(data, 200)
    if args[0] == json_error_1:
        with open("./test/services/scrapers/reverb/dumps/test_bad_1.json",
                  "r", encoding="utf-8") as infile:
            data = json.loads(infile.read())
        # return MockResponse(data, 200)

    return MockResponse(error_code, 404)


class ReverbTests(unittest.TestCase):
    """Test reverb functions."""
    URL = "https://api.reverb.com/api/"

    with open("./test/services/scrapers/reverb/dumps/test_listings.json",
              "r", encoding="utf-8") as infile:
        data = json.load(infile)
        listings: List[Listing] = [Listing(**i) for i in data]

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @mock.patch("services.scrapers.reverb.reverb.requests.get",
                side_effect=mocked_requests_get)
    def test_scrape_reverb(self, mock_get: mock.MagicMock) -> None:
        """Test that the scrape_reverb function returns
        the proper data given a mock request."""
        response = scrape_reverb(self.URL, "electric_guitars", pages=1)
        self.assertIsInstance(response, List)

        for listing in response:
            self.assertIsInstance(listing, Listing)
            self.assertIsInstance(listing.make, str)
        response = scrape_reverb(self.URL, "acoustic_guitars", pages=1)
        self.assertIsInstance(response, List)

        for listing in response:
            self.assertIsInstance(listing, Listing)
            self.assertIsInstance(listing.make, str)

        with self.assertRaises(SystemExit) as c_m:
            scrape_reverb(self.URL + "junk", "electric_guitars", pages=1)
        self.assertEqual(c_m.exception.code,
                         {'Invalid url': ['Url is invalid.']})

        with self.assertRaises(SystemExit) as c_m:
            scrape_reverb("bad1" + self.URL, "electric_guitars")
        self.assertEqual(c_m.exception.code,
                         "Response could not be serialized")

    def test_dump_scrape(self) -> None:
        """Test that the dump_scrape function is properly writing
        data to file."""
        with mock.patch("builtins.open", create=True) as mock_open:
            file_obj = StringIO()
            mock_open.return_value.__enter__.return_value = file_obj
            data = self.listings
            dump_scrape(data, Path("test.json"))

            mock_open.assert_called_once_with(Path("test.json"),
                                              "w", encoding="utf-8")

            file_obj.seek(0)
            file_contents = file_obj.getvalue()
            result = json.loads(file_contents)
            result_listing: List[Listing] = [Listing(**i) for i in result]
            self.assertEqual(result_listing, data)
