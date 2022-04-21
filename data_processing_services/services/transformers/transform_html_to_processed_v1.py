from copy import copy
from typing import Dict

from daos import (
    RawHtmlDocumentRepository as RawRepository,
    ProcessedHtmlV1DocumentRepository as ProcessedHtmlV1Repository,
    DocumentIndexRepository as IndexRepository,
    DocumentIndexModel as IndexModel, DocumentIndexModel,
)

from ..base import (
    threaded_try_except,
    AbstractThreadedService as Base
)

class TransformHtmlToProcessedHtmlV1(Base):
    def __init__(
            self,
            processed_html_v1_repository: ProcessedHtmlV1Repository,
            index_repository: IndexRepository,
            raw_repository: RawRepository
    ):
        super().__init__()
        self.processed_html_v1_repository = processed_html_v1_repository
        self.index_repository = index_repository
        self.raw_repository = raw_repository

    @threaded_try_except
    def run_in_thread(self, task: DocumentIndexModel):
        raw_html_document = self.raw_repository.get(task.document_id)

        if not raw_html_document:
            return

        raw_html_document.load_contents()
        raw_html_document.load_soup()

        soup = copy(raw_html_document.soup)

        attributes_partly_removed = 0
        attributes_fully_removed = 0
        for tag in soup.find_all():
            if tag.name == 'a' and 'href' in tag.attrs:
                href = tag.attrs['href']
                tag.attrs.clear()
                tag['href'] = href
                attributes_partly_removed += 1
            else:
                tag.attrs.clear()
                attributes_fully_removed += 1

        head_tags_removed = 0
        for tag in soup.select('head'):
            tag.decompose()
            head_tags_removed += 1

        script_tags_removed = 0
        for tag in soup.select('script'):
            tag.decompose()
            script_tags_removed += 1

        style_tags_removed = 0
        for tag in soup.select('style'):
            tag.decompose()
            style_tags_removed += 1

        processed_html_v1_document = self.processed_html_v1_repository.create(identifier=raw_html_document.id)
        processed_html_v1_document.contents = str(soup)
        self.processed_html_v1_repository.update(processed_html_v1_document)

        task.processed_html_v1_document_path = processed_html_v1_document.path
        task.is_processed_html_v1_stored = True
        self.index_repository.update(task)

        return {
            'processed_html_v1_path': processed_html_v1_document.path,
            'script_tags_removed': script_tags_removed,
            'head_tags_removed': head_tags_removed,
            'style_tags_removed': style_tags_removed,
            'attributes_fully_removed': attributes_fully_removed,
            'attributes_partly_removed': attributes_partly_removed
        }

    def run(self, params: Dict):
        sync_all = params.get('sync_all', False)
        max_threads = params.get('max_threads', 50)

        if sync_all:
            tasks = self.index_repository.get_all()
        else:
            tasks = self.index_repository.get_all_by_filter({
                IndexModel.is_processed_html_v1_stored: False
            })

        self.run_concurrently_in_threads(tasks, max_threads=max_threads)
        return self.complete()
