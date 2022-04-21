from commons import PdfKit

from daos import *
from dependency_injection import service
from http_server import HttpMethod

from data_processing_services.server.adapter import DataProcessingHttpEndpointServiceAdapter as ServiceAdapter
from data_processing_services.services import (
    ExtractFromProcessedHtmlV1,
    TransformRawHtmlToPdf,
    TransformHtmlToProcessedHtmlV1,
    TransformProcessedHtmlV1ToPdf,
    SyncDocumentIndexDb
)

REPOSITORIES = [
    DocumentIndexRepository,
    ProcessedHtmlV1PdfDocumentRepository,
    ProcessedHtmlV1DocumentRepository,
    RawHtmlDocumentRepository,
    RawHtmlPdfDocumentRepository,
    ProcessedHtmlV1DocumentFeaturesRepository
]

for cls in REPOSITORIES:
    service(cls)

COMMONS_SERVICES = [
    PdfKit
]

for cls in COMMONS_SERVICES:
    service(cls)

SERVICES_PARAMS = [
    ('/extract-from-html-only', HttpMethod.POST, service(ExtractFromProcessedHtmlV1)),
    ('/transform-raw-html-to-pdf', HttpMethod.POST, service(TransformRawHtmlToPdf)),
    ('/transform-html-to-html-only', HttpMethod.POST, service(TransformHtmlToProcessedHtmlV1)),
    ('/transform-html-only-to-pdf', HttpMethod.POST, service(TransformProcessedHtmlV1ToPdf)),
    ('/sync-document-index-db', HttpMethod.POST, service(SyncDocumentIndexDb))
]

SERVICES = [ServiceAdapter(r, m, s()) for r, m, s in SERVICES_PARAMS]
