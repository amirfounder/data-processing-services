from http_server import BaseHttpServer


class DataProcessingHttpServer(BaseHttpServer):
    def __init__(self):
        super().__init__(port=8083)
