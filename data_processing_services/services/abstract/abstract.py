from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict


TRUNCATED_LENGTH = 50


class AbstractDataProcessingService(ABC):
    def __init__(self):
        self.service_suite_id = 'DataProcessingServices'

        self.successful_operations = 0
        self.failed_operations = 0

    def __new__(cls, *args, **kwargs):
        cls.service_id = cls.__name__
        return super().__new__(cls, *args, **kwargs)

    def complete(self):
        return {
            'status': 'DONE',
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations
        }

    @abstractmethod
    def run(self, params: Dict):
        pass
