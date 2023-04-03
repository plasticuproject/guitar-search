"""reverb.py"""

import json
from json import JSONDecodeError
from datetime import datetime
from pathlib import Path
from sys import exit as sys_exit
from typing import List, Optional
import requests
from requests.exceptions import ConnectTimeout
from .reverb_models import Results, Listing

category_uuids = {
    # "guitar_cases": "b1f4ce46-26e5-4f27-8b8a-66bd0f41a8eb",
    # "guitar_gig bags": "9f2edb74-fcd6-41a2-8d25-99222cc2577a",
    # "guitar_strings": "df6f1f19-e67e-42c7-b00b-608cb577edf4",
    "acoustic_guitars": "3ca3eb03-7eac-477d-b253-15ce603d2550",
    # "guitar_cabinets": "f1b3d127-4158-43c3-934b-e402adc3d6ca",
    # "guitar_combos": "10335451-31e5-418a-8ed8-f48cd738f17d",
    # "guitar_heads": "19d53222-297e-410c-ba4f-b48678e917f9",
    # "bass_guitars": "53a9c7d7-d73d-4e7f-905c-553503e50a90",
    # "acoustic_bass_guitars": "bd0f2bd8-714b-4d19-ad87-05c5695a3b02",
    # "guitar_synths": "7e6b6d7c-cdd5-4a42-bceb-6ea12899137b",
    "electric_guitars": "dfd39027-d134-4353-b9e4-57dc6be791b9",
    # "guitarrones": "2b949508-b68d-4456-9353-85cffc9238d7",
    # "bass_guitar parts": "3852c31e-5019-4cd6-8c60-ba5fd397cf43",
    # "guitar_bodies": "92aef906-a2fd-47be-85f5-8595cc61bedb",
    # "guitar_pickups": "ed9714d2-2b98-4e1e-b85e-eb2f948a8985",
}

URL = "https://api.reverb.com/api/"


def scrape_reverb(url: str,
                  instrument: str,
                  pages: Optional[int] = None) -> List[Listing]:
    """
    Scrape reverb.com for listings of supplied instrument type.

    Args:
        url (str): Url for reverb.com API.
        instrument (str): Instrument to scrape listings for.
        pages (Optional[int]): Number of pages of listings to scrape.
            Defaults to None. If default, will scrape all pages plus
            one, floor divided by 50.

    Returns:
        List[reverb_models.Listing]: A list of reverb.com listing dictionaries.

    Raises:
        AssertionError: If any reverb.com API response call reurns anything
            other than a 2xx status code.
        ConnectTimeout: If connection to reverb.com API cannot be made in
            60 seconds or less.
        JSONDecodeError: If the reverb.com API response cannot be serialized
            for any reason.
    """
    uuid = category_uuids[instrument]
    data: List[Listing] = []

    try:
        response = requests.get(f"{url}categories/{uuid}", timeout=60)
        assert response.status_code == 200
        total_pages = (pages + 1 if pages else
                       response.json()["total_pages"] // 50)

    # TODO: Log and handle error
    except AssertionError:
        sys_exit(response.json()["errors"])
    except ConnectTimeout:
        sys_exit('Request has timed out')
    except JSONDecodeError:
        sys_exit("Response could not be serialized")

    for page in range(1, total_pages):

        try:
            response = requests.get(f"{URL}categories/{uuid}?page={str(page)}",
                                    timeout=60)
            assert response.status_code == 200
            results = Results(**response.json())

        # TODO: Log and handle error
        except AssertionError:
            sys_exit(response.json()["errors"])
        except ConnectTimeout:
            sys_exit('Request has timed out')
        except JSONDecodeError:
            sys_exit("Response could not be serialized")

        page_of_listings: List[Listing] = results.listings
        data += page_of_listings

    data.sort(key=lambda listing: datetime.strptime(listing.published_at,
                                                    "%Y-%m-%dT%H:%M:%S%z"),
              reverse=True)

    return data


def dump_scrape(data: List[Listing], file_path: Path) -> None:
    """
    Write scrape data to JSON file.

    Args:
        data (List[reverb_models.Listing]): List of reverb.com
            listing dictionaries.
        file_path (Path): File path to dump JSON data to.

    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as data_file:
        json.dump([i.dict() for i in data],
                  data_file,
                  default=lambda x: x.__dict__,
                  indent=2)
    #  TODO: Save JSON file to blog storage (S3)


if __name__ == "__main__":
    path = Path(__file__).parent
    for catagory in category_uuids:
        dump_scrape(scrape_reverb(URL, catagory),
                    path / "dumps" / f"reverb_{catagory}.json")
