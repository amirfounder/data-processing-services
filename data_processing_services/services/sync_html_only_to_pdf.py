from typing import Dict

import pdfkit

from daos import (
    GoogleSearchResultsHtmlDocumentHtmlOnlyRepository as HtmlOnlyRepository,
    GoogleSearchResultsHtmlDocumentIndexRepository as IndexRepository,
    HtmlDocumentIndexItem as Index,
)

from .abstract import AbstractMultiThreadedDataProcessingService as Base

class SyncHtmlOnlyToPdf(Base):
    def __init__(
            self,
            html_only_repository: HtmlOnlyRepository,
            index_repository: IndexRepository,
    ):
        super().__init__()
        self.html_only_repository = html_only_repository
        self.index_repository = index_repository
        self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    def _run_in_thread(self, item):
        try:

            html_doc = self.html_only_repository.get(item.document_id)
            html_pdf = pdfkit.from_file(html_doc.path, 'lol.pdf', configuration=self.pdfkit_config)

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')

            with self.lock:
                self.service_report.log_failure({
                    'reason': str(e)
                })

    def run(self, params: Dict):
        sync_all = params.get('sync_all', False)
        max_threads = params.get('max_threads', 50)

        items = self.index_repository.get_all() \
            if sync_all \
            else self.index_repository.get_all_by_filter({
                Index.is_no_js_version_stored: True
            })

        self._run_concurrently_in_threads(items, max_threads=max_threads)
        return self.complete()
