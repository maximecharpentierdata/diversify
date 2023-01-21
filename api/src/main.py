import random

from fastapi import Cookie, FastAPI, Request
from mongo import allocation, assets, constraints, database
from optimization import optimization

app = FastAPI()

app.include_router(assets.assets_router)
app.include_router(allocation.allocation_router)
app.include_router(constraints.constraints_router)
app.include_router(optimization.optimization_router)
app.include_router(database.mongo_router)


@app.middleware("http")
async def process_session_cookie(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    response = await call_next(request)
    response.set_cookie(key="session_id", value=session_id)
    return response
