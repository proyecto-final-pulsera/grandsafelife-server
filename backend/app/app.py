"""Punto de composicion y entrada a los casos de uso del servidor."""

from .processes.process_auth import AuthProcesses
from .processes.process_users import UsersProcesses
from .processes.process_homes import HomesProcesses
from .processes.process_devices import DevicesProcesses
from .processes.process_devices_stats import DevicesStatsProcesses
from .processes.process_alarms import AlarmsProcesses
from .processes.process_monitoring_requests import MonitoringRequestsProcesses
from .processes.process_monitoring import MonitoringProcesses
from .processes.process_fall_detection import FallDetectionProcesses


class App:
    """Conserva la interfaz process_* y delega en cada area funcional."""

    def __init__(self, db):
        self.db = db
        self.auth = AuthProcesses(db)
        self.users = UsersProcesses()
        self.homes = HomesProcesses()
        self.devices = DevicesProcesses()
        self.devices_stats = DevicesStatsProcesses()
        self.alarms = AlarmsProcesses()
        self.monitoring_requests = MonitoringRequestsProcesses()
        self.monitoring = MonitoringProcesses()
        self.fall_detection = FallDetectionProcesses()

    def process_login(self, usr, psw):
        return self.auth.process_login(usr, psw)

    def process_get_me(self, authorization):
        return self.auth.process_get_me(authorization)

    def process_get_current_user(self, authorization):
        return self.users.process_get_current_user(authorization)

    def process_get_user_by_id(self, authorization, user_id):
        return self.users.process_get_user_by_id(authorization, user_id)

    def process_get_user_by_email(self, authorization, email):
        return self.users.process_get_user_by_email(authorization, email)

    def process_create_user(self, authorization, user_data):
        return self.users.process_create_user(authorization, user_data)

    def process_update_current_user(self, authorization, user_data):
        return self.users.process_update_current_user(authorization, user_data)

    def process_get_home_by_id(self, authorization, home_id):
        return self.homes.process_get_home_by_id(authorization, home_id)

    def process_create_home(self, authorization, home_data):
        return self.homes.process_create_home(authorization, home_data)

    def process_update_home(self, authorization, home_id, home_data):
        return self.homes.process_update_home(authorization, home_id, home_data)

    def process_delete_home(self, authorization, home_id):
        return self.homes.process_delete_home(authorization, home_id)

    def process_get_device_by_id(self, authorization, device_id):
        return self.devices.process_get_device_by_id(authorization, device_id)

    def process_associate_device(self, authorization, device_id, home_id):
        return self.devices.process_associate_device(authorization, device_id, home_id)

    def process_update_device(self, authorization, device_id, device_data):
        return self.devices.process_update_device(authorization, device_id, device_data)

    def process_release_device(self, authorization, device_id):
        return self.devices.process_release_device(authorization, device_id)

    def process_get_devices_by_owner(self, authorization, owner_id):
        return self.devices.process_get_devices_by_owner(authorization, owner_id)

    def process_get_devices_by_home(self, authorization, home_id):
        return self.devices.process_get_devices_by_home(authorization, home_id)

    def process_get_device_location(self, authorization, device_id):
        return self.devices.process_get_device_location(authorization, device_id)

    def process_get_daily_metrics(self, authorization, device_id, date):
        return self.devices_stats.process_get_daily_metrics(authorization, device_id, date)

    def process_get_monthly_aggregates(self, authorization, device_id, month):
        return self.devices_stats.process_get_monthly_aggregates(authorization, device_id, month)

    def process_get_previous_month_aggregates(self, authorization, device_id):
        return self.devices_stats.process_get_previous_month_aggregates(authorization, device_id)

    def process_get_last_week_metrics(self, authorization, device_id):
        return self.devices_stats.process_get_last_week_metrics(authorization, device_id)

    def process_get_alarms_by_device_id(self, authorization, device_id):
        return self.alarms.process_get_alarms_by_device_id(authorization, device_id)

    def process_set_alarms_by_device_id(self, authorization, device_id, alarms):
        return self.alarms.process_set_alarms_by_device_id(authorization, device_id, alarms)

    def process_create_monitoring_request(self, authorization, home_id, data):
        return self.monitoring_requests.process_create_monitoring_request(authorization, home_id, data)

    def process_get_my_monitoring_requests(self, authorization):
        return self.monitoring_requests.process_get_my_monitoring_requests(authorization)

    def process_answer_monitoring_request(self, authorization, request_id, answer):
        return self.monitoring_requests.process_answer_monitoring_request(authorization, request_id, answer)

    def process_get_monitored_users(self, authorization):
        return self.monitoring.process_get_monitored_users(authorization)

    def process_get_my_monitors(self, authorization):
        return self.monitoring.process_get_my_monitors(authorization)

    def process_delete_monitoring_link(self, authorization, link_id):
        return self.monitoring.process_delete_monitoring_link(authorization, link_id)

    def process_create_fall_detection_request(self, authorization, data):
        return self.fall_detection.process_create_fall_detection_request(authorization, data)

    def process_get_fall_detection_request(self, authorization, request_id):
        return self.fall_detection.process_get_fall_detection_request(authorization, request_id)
