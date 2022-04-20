from __future__ import annotations
from abc import abstractmethod, ABC
from datetime import datetime
from typing import Dict


TRUNCATED_LENGTH = 50


class AbstractDataProcessingService(ABC):
    # noinspection PyTypeChecker
    def __init__(self):
        self.successful_operations = 0
        self.failed_operations = 0

        self.params: Dict = None
        self.start: datetime = None
        self.end: datetime = None
        self.elapsed: datetime = None

    def start_run(self, params: Dict = None):
        self.params = params or {}
        self.successful_operations = 0
        self.failed_operations = 0
        self.start = datetime.now()

    def end_run(self):
        self.end = datetime.now()
        self.elapsed = self.end - self.start

        for k, v in self.params.items():
            if isinstance(v, str) and len(v) > TRUNCATED_LENGTH:
                self.params[k] = v[:TRUNCATED_LENGTH - 3] + '...'

        return {
            'status': 'DONE',
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'performance': {
                'start': self.start.isoformat(),
                'end': self.end.isoformat(),
                'elapsed': str(self.elapsed)
            },
            'params': self.params,
        }

    @abstractmethod
    def run(self, params: Dict):
        pass
