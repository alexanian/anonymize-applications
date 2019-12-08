from __future__ import print_function

import argparse

from googleapiclient.discovery import build
from random_word import RandomWords

from anonymize_applications.auth import get_credentials

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
SAMPLE_RANGE_NAME = "Class Data!A1:E"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Strip identifying information from a Google Sheet."
    )
    parser.add_argument("sheet_id", type=str, help="id of the google sheet to query")
    parser.add_argument("sheet_range", type=str, help="range of sheet to query")
    parser.add_argument(
        "--identifying_cols",
        type=int,
        nargs="+",
        help="a list the 1-indexed numbers of columns with identifying information",
        required=True,
    )
    parser.add_argument(
        "-nh",
        "--no_header",
        action="store_false",
        help="unless set, the first row is assumed to be a header of column names",
        dest="has_header",
    )

    return parser.parse_args()


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    args = parse_args()
    sheet_id = args.sheet_id
    sheet_range = args.sheet_range

    # Call the Sheets API
    service = build("sheets", "v4", credentials=get_credentials())
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    values = result.get("values", [])

    if not values:
        print(f"No values found in range {sheet_range} in sheet {sheet_id}.")
        return

    if args.has_header:
        header = values.pop(0)

    # Write identifying values to a spreadsheet
    random_words = RandomWords().get_random_words(
        hasDictionaryDef=True, includePartOfSpeech="noun", limit=len(values)
    )

    anonymous_ids = [f"{i}_{w}" for i, w in enumerate(random_words)]
    identifying_values = [[v[idx] for idx in args.identifying_cols] for v in values]

    for row in values:
        for col_index, value in enumerate(row):
            if col_index in args.identifying_cols:
                continue

            if header:
                print(header[col_index])

            print(value)


if __name__ == "__main__":
    main()
