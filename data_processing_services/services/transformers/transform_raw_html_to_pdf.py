from typing import Dict

from commons import PdfKit

from daos import (
    RawHtmlDocumentRepository as HtmlRepository,
    RawHtmlPdfDocumentRepository as PdfRepository,
    DocumentIndexRepository as IndexRepository,
    DocumentIndexModel as Index, DocumentIndexModel,
)

from ..base import (
    AbstractThreadedService as Base,
    threaded_try_except
)


class TransformRawHtmlToPdf(Base):
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

    @threaded_try_except
    def run_in_thread(self, item: DocumentIndexModel):
        html_doc = self.html_repository.get(item.document_id)
        pdf_contents = self.pdfkit.from_file(html_doc.path)

        pdf_doc = self.pdf_repository.create(identifier=html_doc.id)
        pdf_doc.contents = pdf_contents
        self.pdf_repository.update(pdf_doc)

        item.raw_html_pdf_version_document_path = pdf_doc.path
        item.is_raw_html_pdf_version_stored = True
        self.index_repository.update(item)

        return {
            'id': item.document_id,
            'html_path': html_doc.path,
            'pdf_path': pdf_doc.path
        }

    def run(self, params: Dict):
        sync_all = params.get('sync_all', False)
        max_threads = params.get('max_threads', 50)

        items = self.index_repository.get_all() \
            if sync_all \
            else self.index_repository.get_all_by_filter({
                Index.is_raw_html_pdf_version_stored: False
            })

        self.run_concurrently_in_threads(items, max_threads=max_threads)
        return self.complete()
