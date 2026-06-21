# database/database.py
from .repositories.users_repository import UsersRepository
from .repositories.monitoring_links_repository import MonitoringLinksRepository
from .repositories.monitoring_requests_repository import MonitoringRequestsRepository

class DataBase:
    def __init__(self):
        self.users = UsersRepository()
        self.links = MonitoringLinksRepository()
        self.requests = MonitoringRequestsRepository()
class DataBase:
    def __init__(self):
        self.users = UsersRepository()
        self.links = MonitoringLinksRepository()
        self.requests = MonitoringRequestsRepository()