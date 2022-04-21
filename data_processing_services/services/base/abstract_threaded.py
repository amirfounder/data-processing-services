from abc import ABC, abstractmethod
from threading import Lock, Thread, enumerate as enumerate_threads
from time import sleep
from typing import Any, List

from .abstract import AbstractService


class AbstractThreadedService(AbstractService, ABC):
    def __init__(self):
        self.lock = Lock()
        self.thread_name = 'DataProcessingThread'
    
    @abstractmethod
    def run_in_thread(self, task: Any):
        pass

    def _active_threads(self):
        return len([thread for thread in enumerate_threads() if thread.name == self.thread_name])

    def run_concurrently_in_threads(self, tasks: List[Any], max_threads: int = 50):
        threads = []

        for item in tasks:
            thread = Thread(
                target=self.run_in_thread,
                args=(item,),
                daemon=True,
                name=self.thread_name
            )
            thread.start()
            threads.append(thread)

            while self._active_threads() >= max_threads:
                sleep(1)

        for thread in threads:
            thread.join()
