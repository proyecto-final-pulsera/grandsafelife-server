# database/database.py

from .users_repository import UsersRepository
from .monitoring_links_repository import MonitoringLinksRepository
from .monitoring_requests_repository import MonitoringRequestsRepository


class DataBase:
    def __init__(self):
        self.users = UsersRepository()
        self.links = MonitoringLinksRepository()
        self.requests = MonitoringRequestsRepository()