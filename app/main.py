from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.request_loggin import RequestLogginMiddleware
from app.tenants.api.routes import router as tenants_router
from app.business.users.api.routes import router as users_router
from app.business.operators.api.routes import router as operators_router
from app.business.verification.api.routes import router as verification_router


app = FastAPI(title="NEXUS API", lifespan=lifespan)

app.add_middleware(RequestLogginMiddleware)

app.include_router(tenants_router)
app.include_router(users_router)
app.include_router(operators_router)
app.include_router(verification_router)