from daos import (
    GoogleSearchResultsHtmlDocumentRawRepository,
    GoogleSearchResultsHtmlDocumentHtmlOnlyRepository,
    GoogleSearchResultsHtmlDocumentIndexRepository,
    GoogleSearchResultsHtmlDocumentNoJSRepository,
)
from dependency_injection import service
from http_server import HttpMethod

from data_processing_services.server.adapter import DataProcessingHttpEndpointServiceAdapter as ServiceAdapter
from data_processing_services.services import *


REPOSITORIES = [
    GoogleSearchResultsHtmlDocumentRawRepository,
    GoogleSearchResultsHtmlDocumentIndexRepository,
    GoogleSearchResultsHtmlDocumentHtmlOnlyRepository,
    GoogleSearchResultsHtmlDocumentNoJSRepository,
]

for cls in REPOSITORIES:
    service(cls)

SERVICES_PARAMS = [
    ('/sync-html-to-no-js', HttpMethod.POST, SyncHtmlToNoJs),
    ('/sync-html-to-html-only', HttpMethod.POST, SyncHtmlToHtmlOnly),
]

SERVICES = [ServiceAdapter(r, m, service(s)()) for r, m, s in SERVICES_PARAMS]
