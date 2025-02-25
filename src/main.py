from fastapi import FastAPI

from src.exceptions.exception_registration import register_exception_handlers
from src.utils.mail import send_mail as mail

VERSION = "v1"
BASE_URL = f"/api/{VERSION}"

app = FastAPI(
    title="Olotooto Server",
    description="This is the server for social media app",
    debug=True,
    contact={"email": "sunarsushil100@gmail.com"},
    version=VERSION,
    docs_url=f"{BASE_URL}/docs",
    root_path=BASE_URL,
)

# registering all the exceptions
register_exception_handlers(app=app)
