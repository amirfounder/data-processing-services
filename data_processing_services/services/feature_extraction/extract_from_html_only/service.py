import timeit
from typing import Dict

from daos import (
    DocumentIndexModel,
    DocumentIndexRepository,
    HtmlOnlyHtmlDocumentRepository,
    HtmlOnlyHtmlDocumentFeaturesRepository
)

from .dataset import DataSet
from ...base import (
    AbstractThreadedService as Base,
    threaded_try_except
)


class ExtractFromHtmlOnly(Base):
    def __init__(
            self,
            index_repository: DocumentIndexRepository,
            html_only_repository: HtmlOnlyHtmlDocumentRepository,
            html_only_feature_repository: HtmlOnlyHtmlDocumentFeaturesRepository
    ):
        super().__init__()
        self.index_repository = index_repository
        self.html_only_repository = html_only_repository
        self.html_only_features_repository = html_only_feature_repository

    @threaded_try_except
    def run_in_thread(self, task: DocumentIndexModel):

        document = self.html_only_repository.get(task.document_id)

        if not document:
            return

        soup = document.load_soup()

        dataset = DataSet()
        for tag in soup.find_all():
            point = dataset.record(tag)
            point.load_features()

        html_only_features = self.html_only_features_repository.create(identifier=document.id)
        html_only_features.contents = dataset.as_features_table()
        html_only_features.flush_contents()

        task.html_only_features_document_path = html_only_features.path
        task.is_html_only_features_stored = True
        self.index_repository.update(task)

        return {
            'data_points': len(html_only_features.contents),
            'features': len(html_only_features.field_names),
            'features_path': html_only_features.path,
        }

    def run(self, params: Dict):
        max_threads = params.get('max_threads', 50)

        tasks = self.index_repository.get_all_by_filter({
            DocumentIndexModel.is_html_only_stored: True,
            DocumentIndexModel.is_html_only_features_stored: False
        })

        self.run_concurrently_in_threads(tasks, max_threads=max_threads)
        return self.complete()

