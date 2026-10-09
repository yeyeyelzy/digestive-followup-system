from fastapi import FastAPI

from .routers.internal_ai import router as internal_ai_router


app = FastAPI(
    title="PCI Rehab Multi-Agent V2 Internal API",
    version="2.1.0",
    description="Internal AI APIs for RuoYi gateway integration",
)


@app.get("/health")
def health() -> dict:
    return {"code": 200, "msg": "success", "data": {"status": "ok", "service": "multi_agent_system_v2_api"}}


app.include_router(internal_ai_router)
