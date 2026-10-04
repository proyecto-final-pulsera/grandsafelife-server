"""Inicialización compartida de Firebase Admin y Cloud Firestore."""
import firebase_admin
from firebase_admin import firestore


def initialize_firebase():
    """Reutiliza la app predeterminada o usa las credenciales del entorno."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        return firebase_admin.initialize_app()


def get_firestore_client():
    return firestore.client(app=initialize_firebase())
