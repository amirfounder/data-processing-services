from daos import (
    NewsArticleHtmlDocumentRawRepository,
    NewsArticleHtmlDocumentHtmlOnlyRepository,
    NewsArticleHtmlDocumentIndexRepository,
    NewsArticleHtmlDocumentNoJsRepository
)
from dependency_injection import service
from http_server import HttpMethod

from data_processing_services.server.adapter import DataProcessingHttpEndpointServiceAdapter as ServiceAdapter
from data_processing_services.services import *


REPOSITORIES = [
    service(NewsArticleHtmlDocumentRawRepository),
    service(NewsArticleHtmlDocumentIndexRepository),
    service(NewsArticleHtmlDocumentHtmlOnlyRepository),
    service(NewsArticleHtmlDocumentNoJsRepository),
]

SERVICES = [
    ServiceAdapter('/clean-html-document-to-no-js', HttpMethod.POST, service(CleanHtmlDocumentToNoJs)()),
    ServiceAdapter('/clean-html-document-to-html-only', HttpMethod.POST, service(CleanHtmlDocumentToHtmlOnly)())
]
