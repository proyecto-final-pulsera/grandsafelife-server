from fastapi import FastAPI
from pydantic import BaseModel

class LoginRequest(BaseModel):
    usr: str
    psw: str

class MonitoringRequestCreate(BaseModel):
    elderly_user_id: int
    requested_user_id: int
    requested_role: str  # admin | monitor

class MonitoringRequestAnswer(BaseModel):
    answer: str  # accepted | rejected

class MonitoringDeleteRequest(BaseModel):
    link_id: int

def create_http_app(system):
    app = FastAPI()

    #==============================================
    # Auth y Login
    #============================================== 
    
    @app.post("/auth/login")
    def login(request: LoginRequest):
        return system.process_login(
            request.usr,
            request.psw
        )

    @app.get("/auth/me")
    def get_me():
        return system.process_get_me()

    #==============================================
    # Monitoreo
    #============================================== 

    @app.get("/monitoring/monitored-users")
    def get_monitored_users():
        return system.process_get_monitored_users()

    @app.get("/monitoring/my-monitors")
    def get_my_monitors():
        return system.process_get_my_monitors()

    #==============================================
    # Requests de monitoreo
    #============================================== 

    @app.post("/monitoring-requests")
    def create_monitoring_request(request: MonitoringRequestCreate):
        return system.process_create_monitoring_request(
            request.elderly_user_id,
            request.requested_user_id,
            request.requested_role
        )

    @app.post("/monitoring-requests/{request_id}/answer")
    def answer_monitoring_request(
        request_id: int,
        request: MonitoringRequestAnswer
    ):
        return system.process_answer_monitoring_request(
            request_id,
            request.answer
        )

    @app.get("/monitoring-requests")
    def get_monitoring_requests():
        return system.process_get_monitoring_requests()

    #==============================================
    # Eliminar monitoreo
    #============================================== 

    @app.delete("/monitoring")
    def delete_monitoring_link(request: MonitoringDeleteRequest):
        return system.process_delete_monitoring_link(
            request.link_id
        )

    return app
