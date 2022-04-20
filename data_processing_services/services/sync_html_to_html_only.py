import threading
from copy import copy
from typing import Dict

from daos import (
    GoogleSearchResultsHtmlDocumentRawRepository as RawRepository,
    GoogleSearchResultsHtmlDocumentHtmlOnlyRepository as HtmlOnlyRepository,
    GoogleSearchResultsHtmlDocumentIndexRepository as IndexRepository,
    HtmlDocumentIndexItem as Index,
)

from .abstract import AbstractMultiThreadedDataProcessingService as Base


class SyncHtmlToHtmlOnly(Base):
    def __init__(
            self,
            html_only_repository: HtmlOnlyRepository,
            index_repository: IndexRepository,
            raw_repository: RawRepository
    ):
        super().__init__()
        self.html_only_repository = html_only_repository
        self.index_repository = index_repository
        self.raw_repository = raw_repository

    def _run_in_thread(self, item):
        try:
            raw_document = self.raw_repository.get(item.document_id)

            if not raw_document:
                return

            raw_document.load_contents()
            raw_document.load_soup()

            soup = copy(raw_document.soup)

            for tag in soup.find_all():
                if hasattr(tag, 'attrs') and isinstance(tag.attrs, dict):
                    tag.attrs.clear()

            for tag in soup.select('script'):
                tag.decompose()

            html_only_document = self.html_only_repository.create(id=raw_document.id)
            html_only_document.contents = str(soup)
            self.html_only_repository.update(html_only_document)

            item.html_only_version_document_path = html_only_document.path
            item.is_html_only_version_stored = True
            self.index_repository.update(item)

            with self.lock:
                self.successful_operations += 1

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')
            with self.lock:
                self.failed_operations += 1

    def run(self, params: Dict):
        items = self.index_repository.get_all_by_filter({
            Index.is_html_only_version_stored: False
        })

        self._run_concurrently_in_threads(items)
        return self.complete()
