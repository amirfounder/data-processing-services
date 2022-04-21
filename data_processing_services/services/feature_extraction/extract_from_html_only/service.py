from typing import Dict
from csv import DictWriter

from daos import (
    DocumentIndexModel,
    DocumentIndexRepository,
    HtmlOnlyHtmlDocumentRepository
)

from .dataset import DataSet
from ...base import (
    AbstractThreadedService as Base,
    threaded_try_except
)


class ExtractFromHtmlOnly(Base):
    def __init__(
            self,
            index_repository: DocumentIndexRepository,
            html_only_repository: HtmlOnlyHtmlDocumentRepository
    ):
        super().__init__()
        self.index_repository = index_repository
        self.html_only_repository = html_only_repository

    @threaded_try_except
    def run_in_thread(self, item: DocumentIndexModel):

        doc_id = item.document_id
        document = self.html_only_repository.get(doc_id)

        if not document:
            return

        document.load_contents()
        document.load_soup()

        soup = document.soup

        dataset = DataSet()
        for tag in soup.find_all():
            point = dataset.record(tag)
            point.load_features()

        features = dataset.as_features_table()
        writer = DictWriter()
        print(len(features))

    def run(self, params: Dict):
        tasks = self.index_repository.get_all_by_filter({
            DocumentIndexModel.is_html_only_stored: True
        })

        self.run_concurrently_in_threads(tasks, max_threads=1)
        return self.complete()

