from typing import Dict

from http_server import BaseHttpEndpointServiceAdapter as BaseAdapter

from data_processing_services.services.abstract import AbstractDataProcessingService as BaseService


class DataProcessingHttpEndpointServiceAdapter(BaseAdapter[BaseService]):
    def run(self, params: Dict):
        return self.service.run(params)
