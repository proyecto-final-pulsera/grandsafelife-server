"""Procesamiento de fall_detection; conserva los mocks y TODO existentes."""


class FallDetectionProcesses:
    def process_create_fall_detection_request(self, authorization, data):
        # TODO: Verificar identidad y permisos, recibir el chunk crudo ya
        # deserializado y solicitar al manager la creación del pedido y su ID.
        # Definir el retorno al implementar el caso de uso.
        pass

    def process_get_fall_detection_request(self, authorization, request_id):
        # TODO: Verificar identidad y acceso al pedido; consultar al manager
        # y retornar su estado, clasificación o error de procesamiento.
        # Definir el retorno al implementar el caso de uso.
        pass
