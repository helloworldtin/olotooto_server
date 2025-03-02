from fastapi import FastAPI

from core.exceptions.exception_registration import register_exception_handlers
from src.auth.routes import auth_router
from src.post.routes import post_router
from src.tag.routes import tag_router
from src.comment.routes import comment_router
from src.like.router import like_router
from src.share.routes import share_router

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
app.include_router(post_router, prefix="/posts", tags=["posts"])
app.include_router(tag_router, prefix="/tags", tags=["tags"])
app.include_router(comment_router, prefix="/comments", tags=["comments"])
app.include_router(like_router, prefix="/likes", tags=["likes"])
app.include_router(share_router, prefix="/shares", tags=["shares"])
