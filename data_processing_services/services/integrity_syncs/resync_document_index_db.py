from typing import Dict, Any

from daos import (
    DocumentIndexRepository,
    RawHtmlDocumentRepository,
    HtmlOnlyHtmlDocumentRepository,
    HtmlOnlyPdfDocumentRepository, DocumentIndexModel
)

from data_processing_services.services.base.abstract_threaded import AbstractThreadedService as Base


class ResyncDocumentIndexDb(Base):
    def __init__(
            self,
            index_repository: DocumentIndexRepository,
            raw_html_repository: RawHtmlDocumentRepository,
            html_only_repository: HtmlOnlyHtmlDocumentRepository,
            html_only_pdf_repository: HtmlOnlyPdfDocumentRepository
    ):
        self.index_repository = index_repository
        self.raw_html_repository = raw_html_repository
        self.html_only_repository = html_only_repository
        self.html_only_pdf_repository = html_only_pdf_repository

    def run_in_thread(self, item: DocumentIndexModel):
        try:

            url: str = item.url
            doc_id = item.document_id

            if not url:
                self.index_repository.delete(item.id)
                self.report.log_failure({
                    'id': item.document_id,
                    'reason': 'No URL present. Could not clean further. Removing item from index ...'
                })
                return

            if 'google.com/search?q=' in url:
                item.is_type_google_search_results = True
                item.google_search_results_query = url.split('&')[0].split('?')[-1].removeprefix('q=').replace('+', ' ')
            else:
                item.is_type_google_search_results = False

            if not doc_id:
                self.report.log_failure({
                    'id': item.document_id,
                    'reason': 'No doc_id present. Could not clean further'
                })
                return

            if raw_document := self.raw_html_repository.get(doc_id):
                item.raw_html_version_document_path = raw_document.path
                item.is_raw_html_version_stored = True
            else:
                item.is_raw_html_version_stored = False

            if html_only_document := self.html_only_repository.get(doc_id):
                item.html_only_version_document_path = html_only_document.path
                item.is_html_only_version_stored = True
            else:
                item.is_html_only_version_stored = False

            if html_only_pdf_document := self.html_only_pdf_repository.get(doc_id):
                item.html_only_pdf_version_document_path = html_only_pdf_document.path
                item.is_html_only_pdf_version_stored = True
            else:
                item.is_html_only_pdf_version_stored = False

            self.index_repository.update(item)
            self.report.log_success({
                'id': item.document_id
            })

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')

            with self.lock:
                self.report.log_failure({
                    'id': item.document_id,
                    'reason': str(e)
                })

    def run(self, params: Dict):
        max_threads = params.get('max_threads', 50)

        items = self.index_repository.get_all()
        self.run_concurrently_in_threads(items, max_threads=max_threads)

        return self.report.complete()
