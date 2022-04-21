from typing import Dict

from daos import DocumentIndexModel, DocumentIndexRepository, HtmlOnlyHtmlDocumentRepository

from ..base.abstract_threaded import AbstractThreadedService as Base


class ExtractFromHtmlOnly(Base):
    def __init__(self, index_repository: DocumentIndexRepository, html_only_repository: HtmlOnlyHtmlDocumentRepository):
        super().__init__()
        self.index_repository = index_repository,
        self.html_only_repository = html_only_repository

    def run_in_thread(self, item: DocumentIndexModel):
        try:

            doc_id = item.document_id
            document = self.html_only_repository.get(doc_id)
            if not document:
                return

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')
            with self.lock:
                self.report.log_failure({
                    'id': item.document_id,
                    'reason': str(e)
                })

    def run(self, params: Dict):
        pass

