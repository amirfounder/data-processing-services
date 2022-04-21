from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict

from data_processing_services.services.abstract.service_report import ServiceReport

TRUNCATED_LENGTH = 50


class AbstractDataProcessingService(ABC):
    service_suit_id = 'DataProcessingServices'

    def __new__(cls, *args, **kwargs):
        cls.service_id = cls.__name__
        cls.service_report = ServiceReport()
        return super().__new__(cls, *args, **kwargs)

    def complete(self):
        return self.service_report.complete()

    @abstractmethod
    def run(self, params: Dict):
        pass
