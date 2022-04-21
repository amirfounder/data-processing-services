from typing import Dict

from daos import (
    DocumentIndexModel,
    DocumentIndexRepository,
    ProcessedHtmlV1DocumentRepository,
    ProcessedHtmlV1DocumentFeaturesRepository
)

from .dataset import DataSet
from ...base import (
    AbstractThreadedService as Base,
    threaded_try_except
)


class ExtractFromProcessedHtmlV1(Base):
    def __init__(
            self,
            index_repository: DocumentIndexRepository,
            processed_html_v1_repository: ProcessedHtmlV1DocumentRepository,
            processed_html_v1_feature_repository: ProcessedHtmlV1DocumentFeaturesRepository
    ):
        super().__init__()
        self.index_repository = index_repository
        self.processed_html_v1_repository = processed_html_v1_repository
        self.processed_html_v1_features_repository = processed_html_v1_feature_repository

    @threaded_try_except
    def run_in_thread(self, task: DocumentIndexModel):

        document = self.processed_html_v1_repository.get(task.document_id)

        if not document:
            path = self.processed_html_v1_repository.path
            doc_id = task.document_id
            raise Exception(f'HTML document was not found : ID: {doc_id}. Path : {path}')

        soup = document.load_soup()

        dataset = DataSet()
        for tag in soup.find_all():
            point = dataset.record(tag)
            point.load_features()

        processed_html_v1_features = self.processed_html_v1_features_repository.create(identifier=document.id)
        processed_html_v1_features.contents = dataset.as_features_table()
        processed_html_v1_features.flush_contents()

        task.processed_html_v1_features_document_path = processed_html_v1_features.path
        task.is_processed_html_v1_features_stored = True
        self.index_repository.update(task)

        return {
            'data_points': len(processed_html_v1_features.contents),
            'features': len(processed_html_v1_features.field_names),
            'features_path': processed_html_v1_features.path,
        }

    def run(self, params: Dict):
        max_threads = params.get('max_threads', 50)
        ignore_filter = params.get('ignore_filter', False)
        specific_id = params.get('specific_id', None)

        if specific_id:
            tasks = [task] if (task := self.index_repository.get(int(specific_id))) else []
        else:
            if ignore_filter:
                tasks = self.index_repository.get_all()
            else:
                tasks = self.index_repository.get_all_by_filter({
                    DocumentIndexModel.is_processed_html_v1_stored: True,
                    DocumentIndexModel.is_processed_html_v1_features_stored: False
                })

        self.run_concurrently_in_threads(tasks, max_threads=max_threads)
        return self.complete()

