from typing import Dict

from daos import (
    DocumentIndexModel,
    DocumentIndexRepository,
    HtmlOnlyHtmlDocumentRepository
)

from ..base import (
    AbstractThreadedService as Base,
    threaded_try_except
)


class ExtractFromHtmlOnlyDocument(Base):
    def __init__(
            self,
            index_repository: DocumentIndexRepository,
            html_only_repository: HtmlOnlyHtmlDocumentRepository
    ):
        super().__init__()
        self.index_repository = index_repository,
        self.html_only_repository = html_only_repository

    @threaded_try_except
    def run_in_thread(self, item: DocumentIndexModel):

        doc_id = item.document_id
        document = self.html_only_repository.get(doc_id)
        if not document:
            return

    def run(self, params: Dict):
        pass

