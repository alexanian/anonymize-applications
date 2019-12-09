from __future__ import print_function

import argparse

from anonymize_gform.response_wrangler import ResponseWrangler
from anonymize_gform.response_writer import ResponseWriter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Strip identifying information from a Google Sheet."
    )
    parser.add_argument("sheet_id", type=str, help="id of the google sheet to query")
    parser.add_argument(
        "--identifying_cols",
        type=int,
        nargs="+",
        help="a list the 1-indexed numbers of columns with identifying information",
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    wrangler = ResponseWrangler(
        response_sheet_id=args.sheet_id, identifying_column_indices=args.identifying_cols
    )

    # Write identifying values to a spreadsheet
    # wrangler.create_identity_sheet()

    # Create google doc
    writer = ResponseWriter()

    doc_id = writer.create(f"{wrangler.anonymous_ids[0]}_responses")
    writer.batchWrite(doc_id, body={})


if __name__ == "__main__":
    main()
