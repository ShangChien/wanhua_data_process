from dotenv import load_dotenv, find_dotenv
# 载入环境变量
load_dotenv(find_dotenv(), override=True)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from .db.utils import DB
import logging,json
from pathlib import Path
import logging.config

# 设置日志
log_config_file = Path(Path(__file__).parent,"log_config.json")
with open(log_config_file, 'r') as f:
    config_dict = json.load(f)
logging.config.dictConfig(config_dict)
logger = logging.getLogger("app")

# 数据库连接和fastapi生命周期钩子销毁连接
DB.connect_db()


@asynccontextmanager
async def lifespan(app):
    await DB.setup_db_index()
    yield
    await DB.close_db()


app = FastAPI(lifespan=lifespan)


# 自定义token认证端点
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API title",
        version="1.0.0",
        description="Your API description",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"][
        "password"
    ]["tokenUrl"] = "/user/token"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def state() -> dict[str, str]:
    logger.info("check app state called")
    return {"state": "ok"}


from .file import file_router
from .task import task_router
from .model import model_router
from .user import user_router

app.include_router(user_router.router)
app.include_router(file_router.router)
app.include_router(task_router.router)
app.include_router(model_router.router)


if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app", host="0.0.0.0", port=7891, log_config=config_dict
    )
