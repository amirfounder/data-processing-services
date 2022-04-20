from typing import Dict

from .base import BaseDataProcessingService as Base


class CleanHtmlDocumentToNoJs(Base):
    def __init__(self):
        super().__init__()

    def run(self, params: Dict):
        pass
