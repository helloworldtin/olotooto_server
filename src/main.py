from fastapi import FastAPI

from src.exceptions.exception_registration import register_exception_handlers
from src.auth.routes import auth_router

VERSION = "v1"
BASE_URL = f"/api/{VERSION}"

app = FastAPI(
    title="Olotooto Server",
    description="This is the server for social media app",
    debug=True,
    contact={"email": "sunarsushil100@gmail.com"},
    version=VERSION,
    root_path=BASE_URL,
)

# registering all the exceptions
register_exception_handlers(app=app)

# adding all the routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
