from typing import Dict

from daos import (
    DocumentIndexRepository,
    RawHtmlDocumentRepository,
    HtmlOnlyHtmlDocumentRepository,
    HtmlOnlyPdfDocumentRepository, DocumentIndexModel
)

from ..base import (
    AbstractThreadedService as Base,
    threaded_try_except
)


class ResyncDocumentIndexDb(Base):
    def __init__(self, index_repository: DocumentIndexRepository, raw_html_repository: RawHtmlDocumentRepository,
                 html_only_repository: HtmlOnlyHtmlDocumentRepository,
                 html_only_pdf_repository: HtmlOnlyPdfDocumentRepository):
        super().__init__()
        self.index_repository = index_repository
        self.raw_html_repository = raw_html_repository
        self.html_only_repository = html_only_repository
        self.html_only_pdf_repository = html_only_pdf_repository

    @threaded_try_except
    def run_in_thread(self, task: DocumentIndexModel):
        url: str = task.url
        doc_id = task.document_id

        if not url:
            self.index_repository.delete(task.id)
            self.report.log_failure({
                'id': task.document_id,
                'reason': 'No URL present. Could not clean further. Removing task from index ...'
            })
            return

        if 'google.com/search?q=' in url:
            task.is_type_google_search_results = True
            task.google_search_results_query = url.split('&')[0].split('?')[-1].removeprefix('q=').replace('+', ' ')
        else:
            task.is_type_google_search_results = False

        if not doc_id:
            self.report.log_failure({
                'id': task.document_id,
                'reason': 'No doc_id present. Could not clean further'
            })
            return

        if raw_document := self.raw_html_repository.get(doc_id):
            task.raw_html_document_path = raw_document.path
            task.is_raw_html_stored = True
        else:
            task.is_raw_html_stored = False

        if html_only_document := self.html_only_repository.get(doc_id):
            task.html_only_document_path = html_only_document.path
            task.is_html_only_stored = True
        else:
            task.is_html_only_stored = False

        if html_only_pdf_document := self.html_only_pdf_repository.get(doc_id):
            task.html_only_pdf_document_path = html_only_pdf_document.path
            task.is_html_only_pdf_stored = True
        else:
            task.is_html_only_pdf_stored = False

        self.index_repository.update(task)
        self.report.log_success({
            'id': task.document_id
        })

    def run(self, params: Dict):
        max_threads = params.get('max_threads', 50)

        tasks = self.index_repository.get_all()
        self.run_concurrently_in_threads(tasks, max_threads=max_threads)

        return self.report.complete()
