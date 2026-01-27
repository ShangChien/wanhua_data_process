from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel
from typing import TypeVar, Generic, cast
from datetime import datetime, timedelta, timezone
from typing import Annotated
from ..db.utils import DB,AsyncIOMotorDatabase

import jwt,os,logging,re
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError,InvalidAlgorithmError
from passlib.context import CryptContext
from .bohrium_auth import is_valid_bohr_token,get_bohr_user_info_by_token,get_bohr_user_info_oauth
logger=logging.getLogger("app")

SECRET_KEY= os.getenv("JWT_SECRET_KEY","")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60*24*7

qsarDB: AsyncIOMotorDatabase = cast(AsyncIOMotorDatabase, DB.db)
user_collection: AsyncIOMotorCollection  = qsarDB['user']
block_token_collection: AsyncIOMotorCollection  = qsarDB['black_tokens']

T = TypeVar("T")
class RES(BaseModel, Generic[T]):
    code: int = 0
    data: T | None = None
    msg: str = ""

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthedUser(BaseModel):
    token:str
    username:str
    user_source_platform:str

class UserInDB(BaseModel):
    username: str
    nickname: str | None = None
    hashed_password: str
    email: str | None = None
    disabled: bool | None = None
    extend: dict|None = None

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

class Password(BaseModel):
    old_password:str
    new_password:str

class UpdatePassword(Password):
    username:str
    
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str) -> str:
    return pwd_context.hash(password)
    
async def get_user(username: str) -> RES[UserInDB] :
    try:
        result= await user_collection.find_one({"username":username},{"_id":0})
        if result is not None:
            return RES(data=UserInDB(**result))
        else:
            logger.error(f"DB get user {username} error")
            return RES(code=-1,msg=f"DB get user {username} error")
    except Exception as e:
        logger.error(f"DB get user {username} error: {e}")
        return RES(code=-1,msg=f"DB get user {username} error: {e}")


def create_access_token(username: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode={
        "sub":username,
        "exp": expire.timestamp(), 
        "ist": datetime.now(timezone.utc).timestamp(),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def register_create_user(data_register:Login) -> RES[str]:
    try:
        if '_' in data_register.username:
            return RES(code=-1,msg=f"用户名不可以包含下划线'_':{data_register.username}")
        new_token= create_access_token(data_register.username)
        hashed_pwd=get_password_hash(data_register.password)
        user=UserInDB(
            username=data_register.username,
            hashed_password=hashed_pwd,
        )
        res = await user_collection.insert_one(user.model_dump())
        logger.info(f"Inserted _id:{res.inserted_id}; username: {data_register.username}; token: {new_token}")
        return RES(data=new_token)
    except DuplicateKeyError:
        return RES(code=-1,msg=f"用户名已存在:{user.username}")
    except Exception as e:
        logger.error(f"db insert error: {e}")
        return RES(code=-1,msg=f"db insert error: {e}")


async def create_user_from_bohr(username:str,password:str) -> RES[bool]:
    try:
        hashed_pwd=get_password_hash( str(password))
        user=UserInDB(
            username=username,
            hashed_password=hashed_pwd,
        )
        res = await user_collection.insert_one(user.model_dump())
        if res.acknowledged:
            logger.info(f"Inserted _id:{res.inserted_id}; username: {username}")
            return RES(data=True)
        else:
            return RES(code=-1,msg=f"db insert bohrium user_info error:{username}")
    except DuplicateKeyError:
        return RES(code=-1,msg=f"用户名已存在:{user.username}")
    except Exception as e:
        logger.error(f"db insert error: {e}")
        return RES(code=-1,msg=f"db insert error: {e}")


async def update_password(data:UpdatePassword) -> RES[bool]:
        res_user_info=await get_user(data.username)
        if res_user_info.code != 0 or not res_user_info.data:
            return RES(code=-1,msg=res_user_info.msg)
        
        if verify_password(data.old_password,res_user_info.data.hashed_password):
            new_hashed_password=get_password_hash(data.new_password)
            try:
                res = await user_collection.update_one(
                    {"username": data.username},
                    {"$set": {"hashed_password": new_hashed_password}}
                )
                if res.acknowledged and res.modified_count==1:
                    logger.info(f"update user: {data.username}'s new_password")
                    return RES(data=True,msg=f"success update {data.username}'s password")
                else:
                    logger.error(f"db error, when update {data.username}'s new_password")
                    return RES(code=-1,msg=f"db error, when update {data.username}'s new_password")
            except Exception as e:
                logger.error(f"fail to update user{data.username} new_password: {e}")
                return RES(code=-1,msg=f"db error, when update {data.username}'s new_password: {e}")
        else:
            logger.error(f"error, {data.username}'s old-password not pass validation")
            return RES(code=-1,msg=f"error, {data.username}'s old-password not pass validation")


async def login_return_token(username: str, password: str) -> RES[str]:
    res_user = await get_user( username)
    if res_user.code != 0 or res_user.data is None:
        return RES(code=-1,msg=f"{username} not exist")
    if not verify_password(password, res_user.data.hashed_password):
        return RES(code=-1,msg="password not valid")
    new_token= create_access_token(username)
    logger.info(f"DB update {username}'s token: {new_token}")
    return RES(data=new_token)


async def is_token_in_blacklist(token:str) -> bool:
    try:
        document = await block_token_collection.find_one({"token": token})
        return document is not None
    except Exception as e:
        logger.error(f"DB check black_token_list error: {e}")
        return False


async def verify_jwt_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AuthedUser:
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_source_platform ='self'

    # 如果jwt解码算法错误，尝试使用bohrium平台非对称jwt认证
    except InvalidAlgorithmError:
        payload=is_valid_bohr_token(token)
        if not payload:
            raise credentials_exception
        bohr_user_info=await get_bohr_user_info_by_token(token)

        if bohr_user_info:
            ## 约定非bohr用户注册时，用户名不可以有下划线'_'
            username: str = bohr_user_info.userName + '_' + str(bohr_user_info.userNo)
            password: str = str(bohr_user_info.userNo) + '@bohr'
            user_source_platform ='bohrium'

            ## 查找用户，如果数据库中不存在该用户则自动注册
            pattern = re.compile(rf'.*_{re.escape(str(bohr_user_info.userNo))}$')
            user=await user_collection.find_one({'username': {'$regex': pattern}})
            if not user:
                res_create = await create_user_from_bohr(username,password)
                if res_create.code != 0:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"fail to register new bohrium user: {res_create.msg}",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                ## 如果用户名和数据库不一致，则更新用户名
                if user['username'] != username:
                    logger.info(f"bohrium username need to be update; old_name: {user['username']} -> new_name: {username}")
                    res_update = await user_collection.update_one(
                        {'username':user['username']},
                        {"$set":{'username':username}}
                    )
                    if res_update.matched_count:
                        logger.info(f"success update bohrium username; old_name: {user['username']} -> new_name: {username}")
                    else:
                        logger.error(f"fail update bohrium username; old_name: {user['username']} -> new_name: {username}")

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"fail to auth bohrium token: {token}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        ## 返回自己的qsar内部管理的token
        token=create_access_token(username)
    #如果token过期无效，直接返回认证失败响应
    except InvalidTokenError:
        raise credentials_exception
    
    is_in_blacklist=await is_token_in_blacklist(token)
    if is_in_blacklist:
        raise credentials_exception
    
    return AuthedUser(username=username,token=token,user_source_platform=user_source_platform)

async def verify_cookie(access_key:str,app_key:str) -> AuthedUser:
    user_info = get_bohr_user_info_oauth(access_key,app_key)

    if user_info is None:
        raise credentials_exception
    
    username: str = user_info.name + '_' + str(user_info.user_id)
    password: str = user_info.user_id + '@bohr'
    user_source_platform ='bohrium'

    ## 查找用户，如果数据库中不存在该用户则自动注册
    pattern = re.compile(rf'.*_{re.escape(str(user_info.user_id))}$')
    user=await user_collection.find_one({'username': {'$regex': pattern}})
    if not user:
        res_create = await create_user_from_bohr(username, password)
        if res_create.code != 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"fail to register new bohrium user: {res_create.msg}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        ## 如果用户名和数据库不一致，则更新用户名
        if user['username'] != username:
            logger.info(f"bohrium username need to be update; old_name: {user['username']} -> new_name: {username}")
            res_update = await user_collection.update_one(
                {'username':user['username']},
                {"$set":{'username':username}}
            )
            if res_update.matched_count:
                logger.info(f"success update bohrium username; old_name: {user['username']} -> new_name: {username}")
            else:
                logger.error(f"fail update bohrium username; old_name: {user['username']} -> new_name: {username}")
                
    token=create_access_token(username)
    return AuthedUser(username=username,token=token,user_source_platform=user_source_platform)
    


async def revoke_token(token:str) -> bool:
    document = {
        "token": token,
        "expireAt": datetime.now(timezone.utc) + timedelta(minutes=7*24*60)
    }
    try:
        result = await block_token_collection.insert_one(document)
        return result.acknowledged
    except Exception as e:
        logger.error(f"DB insert token to black_token_list error: {e}")
        return False
    
