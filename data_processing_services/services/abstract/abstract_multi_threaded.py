import threading
from abc import ABC, abstractmethod
from threading import Thread, Lock
from time import sleep
from typing import Any, List

from .abstract import AbstractDataProcessingService


class AbstractMultiThreadedDataProcessingService(AbstractDataProcessingService, ABC):
    def __new__(cls, *args, **kwargs):
        cls.lock = Lock()
        return super().__new__(cls, *args, **kwargs)

    @abstractmethod
    def _run_in_thread(self, item: Any):
        pass

    def _run_concurrently_in_threads(self, items: List[Any], max_threads: int):
        threads = []

        for i, item in enumerate(items):
            print(f'Starting thread ... {i + 1} / {len(items)}')
            thread = Thread(target=self._run_in_thread, args=(item,), daemon=True, name='DataProcessingThread')
            thread.start()
            threads.append(thread)

            while len([t for t in threading.enumerate() if t.name == 'DataProcessingThread']) >= max_threads:
                sleep(1)

        for thread in threads:
            thread.join()
