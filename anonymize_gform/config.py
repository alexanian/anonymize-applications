# The gspread library uses the drive API, not the sheets API, to create new sheets.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
