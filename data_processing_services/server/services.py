from commons import PdfKit

from daos import *
from dependency_injection import service
from http_server import HttpMethod

from data_processing_services.server.adapter import DataProcessingHttpEndpointServiceAdapter as ServiceAdapter
from data_processing_services.services import *
from data_processing_services.services.save_raw_html_to_pdf import SyncRawHtmlToPdf

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
    ('/sync-raw-html-to-pdf', HttpMethod.POST, service(SyncRawHtmlToPdf)),
    ('/sync-html-to-html-only', HttpMethod.POST, service(SyncHtmlToHtmlOnly)),
    ('/sync-html-only-to-pdf', HttpMethod.POST, service(SyncHtmlOnlyToPdf))
]

SERVICES = [ServiceAdapter(r, m, s()) for r, m, s in SERVICES_PARAMS]
