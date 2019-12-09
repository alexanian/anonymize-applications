from googleapiclient.discovery import build

from .auth import get_credentials


class ResponseWriter:
    def __init__(self):
        self.service = build("docs", "v1", credentials=get_credentials())

    def create(self, title):
        body = {"title": title}

        result = self.service.documents().create(body=body).execute()
        return result["documentId"]

    def batchWrite(self, id, body):
        result = (
            self.service.documents()
            .batchUpdate(documentId=id, body={"requests": body})
            .execute()
        )
        return result
