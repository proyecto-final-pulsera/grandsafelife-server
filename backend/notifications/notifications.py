"""Envío de alertas mediante Firebase Cloud Messaging."""
from firebase_admin import messaging


class Notifications:
    # TODO: Manejar fallos de envío sin propagar una excepción no controlada.
    # Evaluar reintentos cada 15 minutos, persistiendo los envíos pendientes
    # durante un máximo de 24 horas. Distinguir errores transitorios de tokens
    # no registrados (UnregisteredError/NotRegistered) para definir su limpieza.
    def send_fall_notification(self, tokens, home_id, device_uid, name, coords):
        self._send_notification(
            tokens, home_id, device_uid, name, coords,
            event_type="fall_detected", title="Caída detectada",
            body=f"Se detectó una caída: {name}.",
        )

    def send_panic_notification(self, tokens, home_id, device_uid, name, coords):
        self._send_notification(
            tokens, home_id, device_uid, name, coords,
            event_type="panic", title="Botón de pánico",
            body=f"{name} necesita ayuda.",
        )

    def _send_notification(self, tokens, home_id, device_uid, name, coords, *, event_type, title, body):
        for token in tokens:
            messaging.send(messaging.Message(
                token=token,
                notification=messaging.Notification(title=title, body=body),
                data={
                    "home_id": home_id,
                    "type": event_type,
                    "deviceUID": device_uid,
                    "name": name,
                    "lat": str(coords["lat"]),
                    "long": str(coords["long"]),
                },
            ))
