from fastapi import Depends, APIRouter, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from .utils import RES,Login,AuthedUser, UserInDB,Token,get_user,login_return_token,revoke_token,verify_jwt_token,verify_cookie,register_create_user,update_password,UpdatePassword,Password,credentials_exception
from typing import Annotated
import logging

logger =logging.getLogger("app")

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post('/register')
async def register(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]) -> RES[str]:
    try:
        login_data = Login(username=form_data.username, password=form_data.password)
        res = await register_create_user(login_data)
        if res.code == 0:
            logger.info(f'New user registered: {form_data.username}')
            return RES(data=res.data)
        else:
            logger.error(f'user register fail: {form_data.username}')
            return RES(code=-1,msg=f"error: {res.msg}")
    except Exception as e:
        return RES(code=-1,msg=f'error:{e}')

@router.post('/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> RES[str]:
    try:
        res=await login_return_token(username=form_data.username, password=form_data.password)
        if res.code==0:
            logger.info(f'User login: {form_data.username}')
            return RES(data=res.data)
        else:
            logger.error(f'user login fail: {form_data.username}')
            return RES(code=-1,msg=res.msg)
    except Exception as e:
        return RES(code=-1,msg=f'error:{e}')
    
@router.post('/token')
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) ->  Token | None:
    try:
        res=await login_return_token(username=form_data.username, password=form_data.password)
        if res.code==0 and res.data:
            logger.info(f'User login: {form_data.username}')
            return Token(access_token=res.data, token_type="bearer")
        else:
            logger.error(f'user login fail: {form_data.username}')
            raise credentials_exception
    except Exception as e:
        logger.error(f'user login fail: {form_data.username}, error: {e}')
        raise credentials_exception

@router.post('/logout')
async def logout(authed_user: Annotated[AuthedUser, Depends(verify_jwt_token)]) -> RES[bool]:
    try:
        result = await revoke_token(authed_user.token)
        if not result:
            logger.error(f"DB delete {authed_user.username}'s token error")
            return RES(code=-1,msg=f"logout error: DB delete {authed_user.username}'s token error")
        logger.info(f"DB add {authed_user.username}'s token to black_list")
        return RES(data=True,msg="success logout")
    except Exception as e:
        return RES(code=-1,msg=f'error:{e}')
    

@router.post('/change_password')
async def change_password(
    authed_user: Annotated[AuthedUser, Depends(verify_jwt_token)],
    data: Annotated[Password, Body()],
) -> RES[bool]:
    try:
        update_password_data=UpdatePassword(
            username=authed_user.username,
            **data.model_dump()
        )
        res = await update_password(update_password_data)
        if res.code != 0 or not res.data:
            return RES(code=-1,msg=res.msg)
        
        result = await revoke_token(authed_user.token)
        if not result:
            logger.error(f"DB add {authed_user.username}'s token to blacklist error")
            return RES(code=-1,msg=f"DB add {authed_user.username}'s token to blacklist error")
        else:
            logger.info(f"DB add {authed_user.username}'s token to black_list")
            return RES(data=True,msg="success logout")
    except Exception as e:
        return RES(code=-1,msg=f'error:{e}')  

@router.get('/me')
async def get_me(authed_user: Annotated[AuthedUser, Depends(verify_jwt_token)]) -> RES[UserInDB]:
    res_user = await get_user(authed_user.username)
    if res_user.code != 0 or not res_user.data:
        logger.error(f'DB get user data error: {authed_user.username}')
        return RES(code=-1,msg=f'DB get user data error: {authed_user.username};{res_user.msg}')
    return RES(data=res_user.data)
    
@router.get('/token_check')
async def auth_check(authed_user: Annotated[AuthedUser, Depends(verify_jwt_token)]) -> RES[str]:
    res_user = await get_user(authed_user.username)
    if res_user.code != 0 or not res_user.data:
        logger.error(f'fail check token: {authed_user.username}')
        return RES(code=-1,msg=f'fail check token: {authed_user.token}; {authed_user.username}; {res_user.msg}')
    logger.info(f'success check token: {authed_user.token}; {authed_user.username}')
    return RES(data=authed_user.token, msg='token is ok')

class cookieData(BaseModel):
    appAccessKey:str
    clientName:str

@router.post('/get_token_by_cookie')
async def get_token_by_cookie(data: Annotated[cookieData, Body()],) -> RES[str]:
    access_key= data.appAccessKey
    app_key= data.clientName
    if not access_key or not app_key:
        msg=f'access_key and app_key not correct, access__key{access_key}, app_key:{app_key}'
        logger.error(msg)
        return RES(code=-1,msg=msg)
    authed_user = await verify_cookie(access_key,app_key)
    if not authed_user:
        msg=f'fail check token, appAccessKey: {access_key}; clientName: {app_key}'
        logger.error(msg)
        return RES(code=-1,msg=msg)
    
    return RES(data=authed_user.token)