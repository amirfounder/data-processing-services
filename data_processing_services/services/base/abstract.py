from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict

from data_processing_services.services.base.report import Report


class AbstractService(ABC):
    service_suite_id = 'DataProcessingServices'

    def __new__(cls, *args, **kwargs):
        cls.service_id = cls.__name__
        cls.report = Report()
        return super().__new__(cls, *args, **kwargs)

    def complete(self):
        report = self.report.finalize()
        self.report.reset()
        return report

    @abstractmethod
    def run(self, params: Dict):
        pass
