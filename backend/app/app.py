"""Punto de composicion y entrada a los casos de uso del servidor."""

from ..fall_detection.fall_detection_manager import FallProcessorManager

from .processes.process_users import UsersProcesses
from .processes.process_homes import HomesProcesses
from .processes.process_devices import DevicesProcesses
from .processes.process_devices_stats import DevicesStatsProcesses
from .processes.process_alarms import AlarmsProcesses
from .processes.process_fall_detection import FallDetectionProcesses


class App:
    """Conserva la interfaz process_* y delega en cada area funcional."""

    def __init__(self, db, fall_detection_manager: FallProcessorManager | None = None):
        self.db = db
        self.users = UsersProcesses(db)
        self.homes = HomesProcesses(db)
        self.devices = DevicesProcesses(db)
        self.devices_stats = DevicesStatsProcesses(db)
        self.alarms = AlarmsProcesses(db)
        manager = fall_detection_manager if fall_detection_manager is not None else FallProcessorManager(N=1)
        self.fall_detection = FallDetectionProcesses(manager)

    #--------------------
    # Users
    #--------------------
    def process_get_user_by_id(self, user_id):
        return self.users.process_get_user_by_id(user_id)

    def process_get_user_by_email(self, email):
        return self.users.process_get_user_by_email(email)

    def process_create_user(self, user_data, user_id=None):
        return self.users.process_create_user(user_data, user_id)

    def process_update_user(self, user_id, user_data):
        return self.users.process_update_user(user_id, user_data)

    #--------------------
    # Homes
    #--------------------
    def process_get_home_by_id(self, home_id):
        return self.homes.process_get_home_by_id(home_id)

    def process_create_home(self, home_data, home_id=None):
        return self.homes.process_create_home(home_data, home_id)

    def process_update_home(self, home_id, home_data):
        return self.homes.process_update_home(home_id, home_data)

    def process_delete_home(self, home_id):
        return self.homes.process_delete_home(home_id)

    #--------------------
    # Devices
    #--------------------
    def process_get_device_by_id(self, device_id):
        return self.devices.process_get_device_by_id(device_id)

    def process_associate_device(self, authorization, device_id, home_id):
        return self.devices.process_associate_device(authorization, device_id, home_id)

    def process_create_device(self, device_data, device_id=None):
        return self.devices.process_create_device(device_data, device_id)

    def process_update_device(self, device_id, device_data):
        return self.devices.process_update_device(device_id, device_data)

    def process_delete_device(self, device_id):
        return self.devices.process_delete_device(device_id)

    def process_release_device(self, authorization, device_id):
        return self.devices.process_release_device(authorization, device_id)

    def process_get_devices_by_owner(self, owner_id):
        return self.devices.process_get_devices_by_owner(owner_id)

    def process_get_devices_by_home(self, home_id):
        return self.devices.process_get_devices_by_home(home_id)

    def process_get_device_location(self, device_id):
        return self.devices.process_get_device_location(device_id)

    #--------------------
    # Devices Stats
    #--------------------
    def process_get_daily_metrics(self, device_id, date):
        return self.devices_stats.process_get_daily_metrics(device_id, date)

    def process_get_monthly_aggregates(self, device_id, month):
        return self.devices_stats.process_get_monthly_aggregates(device_id, month)

    def process_get_previous_month_aggregates(self, device_id):
        return self.devices_stats.process_get_previous_month_aggregates(device_id)

    def process_get_last_week_metrics(self, device_id):
        return self.devices_stats.process_get_last_week_metrics(device_id)

    #--------------------
    # Alarms
    #--------------------
    def process_get_alarms_by_device_id(self, device_id):
        return self.alarms.process_get_alarms_by_device_id(device_id)

    def process_set_alarms_by_device_id(self, device_id, alarms):
        return self.alarms.process_set_alarms_by_device_id(device_id, alarms)

    #--------------------
    # Fall Detection
    #--------------------
    def process_create_fall_detection_request(self, authorization, data):
        return self.fall_detection.process_create_fall_detection_request(authorization, data)

    def process_get_fall_detection_request(self, authorization, request_id):
        return self.fall_detection.process_get_fall_detection_request(authorization, request_id)
