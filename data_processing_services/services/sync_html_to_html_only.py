from copy import copy
from typing import Dict

from daos import (
    RawHtmlDocumentRepository as RawRepository,
    HtmlOnlyHtmlDocumentRepository as HtmlOnlyRepository,
    DocumentIndexRepository as IndexRepository,
    DocumentIndexModel as IndexModel,
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
            raw_html_document = self.raw_repository.get(item.document_id)

            if not raw_html_document:
                return

            raw_html_document.load_contents()
            raw_html_document.load_soup()

            soup = copy(raw_html_document.soup)

            attributes_removed = 0
            for tag in soup.find_all():
                tag.attrs.clear()
                attributes_removed += 1

            head_tags_removed = 0
            for tag in soup.select('head'):
                tag.decompose()
                head_tags_removed += 1

            script_tags_removed = 0
            for tag in soup.select('script'):
                tag.decompose()
                script_tags_removed += 1

            html_only_document = self.html_only_repository.create(identifier=raw_html_document.id)
            html_only_document.contents = str(soup)
            self.html_only_repository.update(html_only_document)

            item.html_only_version_document_path = html_only_document.path
            item.is_html_only_version_stored = True
            self.index_repository.update(item)

            with self.lock:
                self.service_report.log_success({
                    'id': item.document_id,
                    'raw_html_path': raw_html_document.path,
                    'html_only_path': html_only_document.path,
                    'script_tags_removed': script_tags_removed,
                    'head_tags_removed': head_tags_removed,
                    'attributes_removed': attributes_removed
                })

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')
            with self.lock:
                self.service_report.log_failure({
                    'id': item.document_id,
                    'reason': str(e)
                })

    def run(self, params: Dict):
        sync_all = params.get('sync_all', False)
        max_threads = params.get('max_threads', 50)

        items = self.index_repository.get_all() \
            if sync_all \
            else self.index_repository.get_all_by_filter({
                IndexModel.is_html_only_version_stored: False
            })

        self._run_concurrently_in_threads(items, max_threads=max_threads)
        return self.complete()
