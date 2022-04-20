from abc import abstractmethod, ABC
from typing import Dict


class BaseDataProcessingService(ABC):
    def __init__(self):
        self.successful_operations = 0
        self.failed_operations = 0

    @abstractmethod
    def run(self, params: Dict):
        self.successful_operations = 0
        self.failed_operations = 0
