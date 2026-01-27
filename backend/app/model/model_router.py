from fastapi import APIRouter,Depends
from .utils import RES,available_models,TaskOut
from .chart import chart_router
import logging
from typing import Annotated
from ..user.utils import verify_jwt_token,AuthedUser

logger = logging.getLogger("app")

router = APIRouter(
    prefix="/model",
    tags=["model"],
)

router.include_router(chart_router.router)

@router.get('/available_models')
async def get_available_models(
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[list[TaskOut]]:
    try:
        models = await available_models(user.username)
        return RES(data=models)
    except Exception as e:
        return RES(code=-1,msg=f'error:{e}')

 