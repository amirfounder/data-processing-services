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
    service(GoogleSearchResultsHtmlDocumentRawRepository),
    service(GoogleSearchResultsHtmlDocumentIndexRepository),
    service(GoogleSearchResultsHtmlDocumentHtmlOnlyRepository),
    service(GoogleSearchResultsHtmlDocumentNoJSRepository),
]

SERVICES = [
    ServiceAdapter('/clean-html-document-to-no-js', HttpMethod.POST, service(CleanHtmlDocumentToNoJs)()),
    ServiceAdapter('/clean-html-document-to-html-only', HttpMethod.POST, service(CleanHtmlDocumentToHtmlOnly)())
]
