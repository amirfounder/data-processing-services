import threading
import time
from copy import copy
from typing import Dict

from daos import (
    GoogleSearchResultsHtmlDocumentRawRepository as RawRepository,
    GoogleSearchResultsHtmlDocumentNoJSRepository as NoJsRepository,
    GoogleSearchResultsHtmlDocumentIndexRepository as IndexRepository,
    HtmlDocumentIndexItem as Index,
)

from .base import BaseDataProcessingService as Base


class SyncHtmlToNoJs(Base):
    def __init__(
            self,
            no_js_repository: NoJsRepository,
            index_repository: IndexRepository,
            raw_repository: RawRepository
    ):
        super().__init__()
        self.no_js_repository = no_js_repository
        self.index_repository = index_repository
        self.raw_repository = raw_repository
        self.lock = threading.Lock()

    def run_in_thread(self, item):
        try:
            raw_document = self.raw_repository.get(item.document_id)

            if not raw_document:
                return

            raw_document.load_contents()
            raw_document.load_soup()

            soup = copy(raw_document.soup)

            for tag in soup.select('script'):
                tag.decompose()

            no_js_document = self.no_js_repository.create(id=raw_document.id)
            no_js_document.contents = str(soup)
            self.no_js_repository.update(no_js_document)

            item.no_js_version_document_path = no_js_document.path
            item.is_no_js_version_stored = True
            self.index_repository.update(item)

            with self.lock:
                self.successful_operations += 1

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')
            with self.lock:
                self.failed_operations += 1

    def run(self, params: Dict):
        self.reset_operation_counters()
        items = self.index_repository.get_all_by_filter({
            Index.is_no_js_version_stored: False
        })
        print(f'Identified {len(items)} html documents to clean ...')

        threads = []

        for i, item in enumerate(items):
            print(f'Starting thread ... {i + 1} / {len(items)}')
            thread = threading.Thread(target=self.run_in_thread, args=(item,), daemon=True)
            thread.start()
            threads.append(thread)

            while threading.active_count() >= 20:
                time.sleep(1)

        for thread in threads:
            thread.join()

        return {
            'status': 'DONE',
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations
        }
