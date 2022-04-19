from copy import copy
from typing import Dict, List

from daos import (
    NewsArticleHtmlDocumentRawRepository as RawRepository,
    NewsArticleHtmlDocumentHtmlOnlyRepository as HtmlOnlyRepository,
    NewsArticleHtmlDocumentHtmlOnlyModel as HtmlOnlyModel,
    NewsArticleHtmlDocumentIndexRepository as IndexRepository,
    NewsArticleHtmlDocumentIndexModel as Index,
    NewsArticleHtmlDocumentIndexFilter as Filter
)

from .base import BaseDataProcessingService as Base


class CleanHtmlDocumentToHtmlOnly(Base):
    def __init__(
            self,
            html_only_repository: HtmlOnlyRepository,
            index_repository: IndexRepository,
            raw_repository: RawRepository
    ):
        self.html_only_repository = html_only_repository
        self.index_repository = index_repository
        self.raw_repository = raw_repository

    def run(self, params: Dict):
        _filter = Filter({Index.is_html_only_version_stored: False})
        indices: List[Index] = self.index_repository.get_all_by_filter(_filter)

        for index in indices:
            raw_document = self.raw_repository.get_by_path(index.raw_version_document_path)
            raw_document.load_soup()

            soup = copy(raw_document.soup)

            for tag in soup.find_all():
                if hasattr(tag, 'attrs') and isinstance(tag.attrs, dict):
                    tag.attrs.clear()

            for tag in soup.select('script'):
                tag.decompose()

            html_only_document = HtmlOnlyModel(soup)
            html_only_document.set_id(raw_document.get_id())
            self.html_only_repository.save(html_only_document)

            index.html_only_version_document_path = str(html_only_document.get_path())
            index.is_html_only_version_stored = True

            self.index_repository.update(index)

        return {
            'status': 'SUCCESS'
        }
