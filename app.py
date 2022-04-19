from data_processing_services import DataProcessingHttpServer, SERVICES

if __name__ == '__main__':
    server = DataProcessingHttpServer()
    server.register_services(SERVICES)
    server.run()
