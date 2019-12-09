from datetime import datetime
from random import shuffle
from typing import List

import gspread
from random_word import RandomWords

from .auth import get_gspread_credentials


class ResponseWrangler:
    """
    So you got some applications sent in through a Google Form and now you want to anonymize
    them. Valid!
    """

    def __init__(
        self,
        response_sheet_id: str,
        identifying_column_indices: List[int],
        share_with: str = None,
    ):
        """
        :param response_sheet_id:
        :param identifying_column_indices:
        """
        self.service = gspread.authorize(get_gspread_credentials())

        # We're assuming you're using the default output of a google form, so just get sheet 1
        self.sheet = self.service.open_by_key(response_sheet_id).sheet1

        # Read the values in the sheet
        values = self.sheet.get_all_values()
        self.headers = values[0]

        # Randomize the row order once
        self.values = values[1:]
        shuffle(self.values)

        self.identifying_indices = identifying_column_indices

    @property
    def identifying_values(self):
        if not getattr(self, "_id_values", None):
            self._id_values = [
                [v[i] for i in self.identifying_indices] for v in self.values
            ]

        return self._id_values

    @property
    def anonymized_values(self):
        if not getattr(self, "_anon_values", None):
            all_indices = set(range(len(self.values[0])))
            anon_indices = all_indices.difference(self.identifying_indices)
            self._anon_values = [[v[i] for i in anon_indices] for v in self.values]

        return self._anon_values

    @property
    def headers_for_anonymized_values(self):
        if not getattr(self, "_anon_headers", None):
            all_indices = set(range(len(self.values[0])))
            anon_indices = all_indices.difference(self.identifying_indices)
            self._anon_headers = [self.headers[i] for i in anon_indices]

        return self._anon_headers

    @property
    def anonymous_ids(self):
        if not getattr(self, "_anonymous_ids", None):
            # Get anonymous ids for each person - #_word
            random_words = RandomWords().get_random_words(
                hasDictionaryDef=True,
                includePartOfSpeech="noun",
                limit=len(self._id_values),
            )

            self._anonymous_ids = [[f"{i}_{w}"] for i, w in enumerate(random_words)]

        return self._anonymous_ids

    def create_identity_sheet(self, title: str = None) -> str:
        """
        Create a new speadsheet that will act as a key between anonymized ids and the information
        identifying applicants.

        :param identifying_values: values extracted from the spreadsheet that identify applicants.
        :param title: If not provided, sheet will be titled
            "anonymized_applications_key_[datetime]", with the datetime format YYYY-mm-dd_ssssss.
        :returns: a list of anonymous ids, corresponding to every row in identifying_values.
        """
        if title is None:
            title = (
                f"anonymized_applications_key_{datetime.now().strftime('%Y-%m-%d_%f')}"
            )

        created = self.service.create(title)

        num_rows = len(self.identifying_values)
        num_cols = len(self.identifying_values[0])

        # Format information for update - first dictionary adds the headers, second dictionary
        # adds the column of anonymized ids, and third adds the identifying information
        batch_update_data = [
            {
                "range": f"Sheet1!A1:{gspread.utils.rowcol_to_a1(1, num_cols + 1)}",
                "majorDimension": "COLUMNS",
                "values": [["id"]] + [[self.headers[idx]] for idx in self.identifying_indices],
            },
            {
                "range": f"Sheet1!A2:{gspread.utils.rowcol_to_a1(num_rows + 1, 1)}",
                "majorDimension": "ROWS",
                "values": self.anonymous_ids,
            },
            {
                "range": f"Sheet1!B2:{gspread.utils.rowcol_to_a1(num_rows + 1, num_cols + 1)}",
                "majorDimension": "ROWS",
                "values": self.identifying_values,
            },
        ]

        # Fill in the spreadsheet
        result = created.values_batch_update(
            body={"valueInputOption": "RAW", "data": batch_update_data}
        )

        return result["spreadsheetId"]
