from typing import Dict

import imgkit

from daos import (
    GoogleSearchResultsHtmlDocumentNoJSRepository as NoJsRepository,
    GoogleSearchResultsHtmlDocumentIndexRepository as IndexRepository,
    HtmlDocumentIndexItem as Index,
)

from .abstract import AbstractMultiThreadedDataProcessingService as Base

class SyncNoJsToPng(Base):
    def __init__(
            self,
            no_js_repository: NoJsRepository,
            index_repository: IndexRepository,
    ):
        super().__init__()
        self.no_js_repository = no_js_repository
        self.index_repository = index_repository
        self.imgkit_config = imgkit.config(wkhtmltoimage=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe')
        self.imgkit_options = {
            "enable-local-file-access": None
        }

    def _run_in_thread(self, item):
        try:

            html_doc = self.no_js_repository.get(item.document_id)
            html_img = imgkit.from_file(
                html_doc.path,
                'lol.png',
                config=self.imgkit_config,
                options=self.imgkit_options
            )

            print('lol')

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {item.document_id}')

            with self.lock:
                self.operations_report.log_failure({
                    'reason': str(e)
                })

    def run(self, params: Dict):
        sync_all = params.get('sync_all', False)

        items_filter = {Index.is_html_only_version_stored: True}

        if sync_all:
            items = self.index_repository.get_all()
        else:
            items = self.index_repository.get_all_by_filter(items_filter)

        self._run_concurrently_in_threads(items, max_threads=1)
        return self.complete()
