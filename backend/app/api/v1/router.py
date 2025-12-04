"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    servers,
    configs,
    orders,
    tickets,
    finance,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(servers.router, prefix="/servers", tags=["Servers"])
api_router.include_router(configs.router, prefix="/configs", tags=["Configs"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(finance.router, prefix="/finance", tags=["Finance"])

