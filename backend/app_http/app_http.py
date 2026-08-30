from fastapi import FastAPI, Header
from pydantic import BaseModel
#from database/usersDB/repositories/users_repository.py import UsersRepository

#==============================================
# API Rest
#============================================== 
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
    def get_me(authorization: str | None = Header(default=None)):
        return system.process_get_me(authorization)

    #==============================================
    # Monitoreo- Typescript / Nest - Inyeccion dependencias
    #============================================== 

    @app.get("/monitoring/monitored-users")
    def get_monitored_users(authorization: str | None = Header(default=None)):
        return system.process_get_monitored_users(authorization)

    @app.get("/monitoring/my-monitors")
    def get_my_monitors(authorization: str | None = Header(default=None)):
        return system.process_get_my_monitors(authorization)

    #==============================================
    # Requests de monitoreo
    #============================================== 

    @app.post("/monitoring-requests")
    def create_monitoring_request(
        request: MonitoringRequestCreate,
        authorization: str | None = Header(default=None)
    ):
        return system.process_create_monitoring_request(
            authorization,
            request.monitored_user_id,
            request.requested_user_id,
            request.requested_role
        )

    @app.post("/monitoring-requests/{request_id}/answer")
    def answer_monitoring_request(
        request_id: int,
        request: MonitoringRequestAnswer,
        authorization: str | None = Header(default=None)
    ):
        return system.process_answer_monitoring_request(
            authorization,
            request_id,
            request.answer
        )

    @app.get("/monitoring-requests")
    def get_monitoring_requests(authorization: str | None = Header(default=None)):
        return system.process_get_monitoring_requests(authorization)

    #==============================================
    # Eliminar monitoreo
    #============================================== 

    @app.delete("/monitoring")
    def delete_monitoring_link(
        request: MonitoringDeleteRequest,
        authorization: str | None = Header(default=None)
    ):
        return system.process_delete_monitoring_link(
            authorization,
            request.link_id
        )

    return app

#==============================================
# Mappers
#============================================== 

class LoginRequest(BaseModel):
    usr: str
    psw: str

class MonitoringRequestCreate(BaseModel):
    monitored_user_id: int
    requested_user_id: int
    requested_role: str  # admin | monitor

class MonitoringRequestAnswer(BaseModel):
    answer: str  # accepted | rejected

class MonitoringDeleteRequest(BaseModel):
    link_id: int