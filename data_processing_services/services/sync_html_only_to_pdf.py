from typing import Dict

from commons import PdfKit

from daos import (
    HtmlOnlyHtmlDocumentRepository as HtmlRepository,
    HtmlOnlyPdfDocumentRepository as PdfRepository,
    DocumentIndexRepository as IndexRepository,
    DocumentIndexModel as Index,
)

from .abstract import AbstractMultiThreadedDataProcessingService as Base

class SyncHtmlOnlyToPdf(Base):
    def __init__(
            self,
            pdfkit: PdfKit,
            html_repository: HtmlRepository,
            pdf_repository: PdfRepository,
            index_repository: IndexRepository,
    ):
        super().__init__()
        self.html_repository = html_repository
        self.pdf_repository = pdf_repository
        self.index_repository = index_repository
        self.pdfkit = pdfkit

    def _run_in_thread(self, item):
        try:

            html_doc = self.html_repository.get(item.document_id)
            html_pdf = self.pdfkit.from_file(html_doc.path)

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
                Index.is_pdf_version_stored: False
            })

        self._run_concurrently_in_threads(items, max_threads=max_threads)
        return self.complete()
