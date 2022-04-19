from abc import abstractmethod, ABC
from typing import Dict


class BaseDataProcessingService(ABC):

    @abstractmethod
    def run(self, params: Dict):
        pass
