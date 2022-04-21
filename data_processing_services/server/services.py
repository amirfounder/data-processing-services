from commons import PdfKit

from daos import *
from dependency_injection import service
from http_server import HttpMethod

from data_processing_services.server.adapter import DataProcessingHttpEndpointServiceAdapter as ServiceAdapter
from data_processing_services.services import *

REPOSITORIES = [
    DocumentIndexRepository,
    HtmlOnlyPdfDocumentRepository,
    HtmlOnlyHtmlDocumentRepository,
    RawHtmlDocumentRepository,
    RawHtmlPdfDocumentRepository
]

for cls in REPOSITORIES:
    service(cls)

COMMON_SERVICES = [
    PdfKit
]

for cls in COMMON_SERVICES:
    service(cls)

SERVICES_PARAMS = [
    ('/transform-raw-html-to-pdf', HttpMethod.POST, service(TransformRawHtmlToPdf)),
    ('/transform-html-to-html-only', HttpMethod.POST, service(TransformHtmlToHtmlOnly)),
    ('/transform-html-only-to-pdf', HttpMethod.POST, service(TransformHtmlOnlyToPdf)),
    ('/resync-document-index-db', HttpMethod.POST, service(ResyncDocumentIndexDb))
]

SERVICES = [ServiceAdapter(r, m, s()) for r, m, s in SERVICES_PARAMS]
