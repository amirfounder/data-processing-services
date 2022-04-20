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
    ('/clean-html-document-to-no-js', HttpMethod.POST, CleanHtmlDocumentToNoJs),
    ('/clean-html-document-to-html-only', HttpMethod.POST, CleanHtmlDocumentToHtmlOnly),
]

SERVICES = [ServiceAdapter(r, m, service(s)()) for r, m, s in SERVICES_PARAMS]
