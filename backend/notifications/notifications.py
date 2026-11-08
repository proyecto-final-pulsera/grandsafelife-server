"""Envío de alertas de caída mediante Firebase Cloud Messaging."""
from firebase_admin import messaging


class Notifications:
    # TODO: Manejar fallos de envío sin propagar una excepción no controlada.
    # Evaluar reintentos cada 15 minutos, persistiendo los envíos pendientes
    # durante un máximo de 24 horas. Distinguir errores transitorios de tokens
    # no registrados (UnregisteredError/NotRegistered) para definir su limpieza.
    def send_fall_notification(self, tokens, home_id, device_uid, name, coords):
        for token in tokens:
            messaging.send(messaging.Message(
                token=token,
                notification=messaging.Notification(
                    title="Caída detectada",
                    body=f"Se detectó una caída: {name}.",
                ),
                data={
                    "home_id": home_id,
                    "type": "fall_detected",
                    "deviceUID": device_uid,
                    "name": name,
                    "lat": str(coords["lat"]),
                    "long": str(coords["long"]),
                },
            ))
