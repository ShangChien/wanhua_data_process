from dataclasses import dataclass
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Body,HTTPException,status,Request
from typing import Any, Annotated,cast,Literal
from pathlib import Path
import logging,os
from asyncio import Semaphore
from ..user.utils import verify_jwt_token,AuthedUser
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from ..db.utils import DB,AsyncIOMotorDatabase
from .utils import RES,InFit,InInfer,TaskType
from .task_manager import Task,TaskInDB,DB_Operation as OP
from .deliver_token_utils import decrypt_and_validate

logger = logging.getLogger("app")

router = APIRouter(
    prefix="/task",
    tags=["task"],
)

sem = Semaphore(1)
qsarDB: AsyncIOMotorDatabase = cast(AsyncIOMotorDatabase, DB.db)
user_collection: AsyncIOMotorCollection  = qsarDB['user']
task_collection: AsyncIOMotorCollection  = qsarDB['task']

# raw_files, valid_files
FILES_DIR       = "/vepfs/fs_users/chensq/project/data_uniqsar/files"
MODELS_DIR      = "/vepfs/fs_users/chensq/project/data_uniqsar/models"

@router.post("/new_train")
async def new_train(
    data: Annotated[InFit, Body()],
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[str]:
    try:
        files = list(Path(FILES_DIR, "valid_files").glob(pattern=f"{data.file_id}_*"))
        ## 如果文件存在
        if len(files) == 1:
            ## 实例化task
            task = Task(
                name=data.name,
                owner=user.username,
                type=TaskType(fit=data),
                model_task=data.config_dict["Base"]["task"],
                config_dict=data.config_dict,
                data_path=files[0],
            )
            ## db写入任务
            res = await OP.commit_task(task)
            if res:
                return RES(data=f'run_id: {res}', msg="success add train task")
            else:
                return RES(code=-1, msg="DB fail add train task")
        else:
            return RES(code=-1, msg=f"fail to get train file: {data.file_id}")
    except Exception as e:
        return RES(code=-1, msg=f"fail add train task: {e}")


@router.post("/new_infer")
async def new_infer(
    data: Annotated[InInfer, Body()],
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[str]:
    try:
        ## 重写前端的传参数
        data.smiles_col = data.smiles_col if data.smiles_col else "SMILES"
        
        res_db = await task_collection.find_one({"_id":ObjectId(data.model_trained_run_id)})
        ## 检查模型是否可用
        if not res_db:
            return RES(code=-1,msg=f'not found task trained model with run_id:{data.model_trained_run_id}')
        model_trained=TaskInDB(**TaskInDB.db_raw2Task(res_db))
        if model_trained.status != 'FINISHED':
            return RES(code=-1,msg=f'{data.model_trained_run_id} task status is {model_trained.status}')
        
        files = list(Path(FILES_DIR, "valid_files").glob(pattern=f"{data.file_id}_*"))
        if len(files) == 1:
            if files[0].suffix == ".csv" and data.smiles_col is None:
                return RES(
                    code=-1,
                    msg="predict source file is .CSV format, field smiles_col is required",
                )
            
            ## 实例化task
            task = Task(
                name=data.name,
                owner=user.username,
                type=TaskType(infer=data),
                model_task=model_trained.model_task,
                data_path=files[0]
            )
            ## db写入任务
            res = await OP.commit_task(task)
            if res:
                return RES(data=f'run_id: {res}', msg="success add predict task")
            else:
                return RES(code=-1, msg="DB fail add predict task")
        else:
            return RES(code=-1, msg=f"fail to get predict file: {data.file_id}")
    except Exception as e:
        return RES(code=-1, msg=f"submit predict task error:{e}")


class TaskId(BaseModel):
    run_id: str


@router.post("/stop")
async def kill_task(
    data: Annotated[TaskId, Body()],
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[bool]:
    try:
        task=await OP.get_task_info(data.run_id)
        if not task:
            return RES(code=-1,msg=f'no run_id task: {data.run_id}')
        if task.owner != user.username:
            return RES(code=-1,msg='permission error')
        
        res: RES[bool]=await OP.stop(data.run_id)
        if res.code == 0:
            return RES(data=True, msg=res.msg)
        else:
            return RES(code=-1, msg=res.msg)
    except Exception as e:
        return RES(code=-1, msg=f"error: {e}")


@router.post("/remove")
async def rm_task(
    data: Annotated[TaskId, Body()],
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[bool]:
    try:
        task=await OP.get_task_info(data.run_id)
        if not task:
            return RES(code=-1,msg=f'no run_id task: {data.run_id}')
        
        logger.info(task.to_dict())
        if task.owner != user.username:
            return RES(code=-1,msg='permission error')
        logger.info(f'准备删除{data.run_id}')
        res = await OP.rm_task(data.run_id)
        if res.code == 0:
            return RES(data=True, msg=res.msg)
        else:
            return RES(code=-1, msg=res.msg)
    except Exception as e:
        return RES(code=-1, msg=f"rm error: {e}")


@router.get("/list")
async def get_task_list(
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[Any]:
    try:
        logger.info(f'user:{user.username} fetch task list')
        task_list_info = await OP.get_task_list_info(user.username)
        return RES(data=task_list_info)
    except Exception as e:
        return RES(code=-1, msg=f"error:{e}")


@router.post("/log")
async def get_task_log(
    data: Annotated[TaskId, Body()],
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[Any]:
    try:
        task=await OP.get_task_info(data.run_id)
        if not task:
            return RES(code=-1,msg=f'no run_id task: {data.run_id}')
        if task.owner != user.username:
            return RES(code=-1,msg='permission error')
        
        sub_dir= "783693552791073446" if task.type.fit else "639031919007598614"
        log_file_path= Path(MODELS_DIR, sub_dir, data.run_id, 'qsar_runtime.log')
        if log_file_path.exists():
            with open(log_file_path, "r") as f:
                content = f.read()
            return RES(data=content)
        else:
            return RES(code=-1, msg=f"not found log_file: {data.run_id}")
    except Exception as e:
        return RES(code=-1, msg=f"error:{e}")


@router.post("/get_by_run_id")
async def get_task(
    data: Annotated[TaskId, Body()],
    user: Annotated[AuthedUser,Depends(verify_jwt_token)]
) -> RES[Any]:
    try:
        task=await OP.get_task_info(data.run_id)
        if not task:
            return RES(code=-1,msg=f'no run_id task: {data.run_id}')
        if task.owner != user.username:
            return RES(code=-1,msg='permission error')
        
        task_type_infer=task.type.model_dump()['infer']

        task_info = {
            "metrics": task.metrics,
            "params": task.params,
            "task_type":task.type,
            "model_task":task.model_task,
            "data_path":task.data_path.name,
            "name": task.name,
            "status": task.status,
            "start_time": task.exec_time,
            "end_time": task.end_time,
            "model_trained_run_id": task_type_infer['model_trained_run_id'] if task_type_infer  else ''
        }
        return RES(data=task_info)
    except Exception as e:
        return RES(code=-1, msg=f"error:{e}")



@dataclass
class WorkerInfo:
    machine_ip:str
    token:str

class TaskDeliver(TaskType):
    run_id:str

@router.post('/acquire_task')
async def acquire_task(
    worker_info:Annotated[WorkerInfo, Body()],
    req:Request
) -> RES[TaskDeliver]:
    try:
        logger.info(f'get worker request: {req.client}')
        if not decrypt_and_validate(worker_info.token,password=os.getenv("WORKER_PASSWORD","uni_qsar")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"fail to check worker token: {worker_info.token}",
            )
        logger.info('worker request pass validate')
        async with sem:
            task = await OP.deliver_task(worker_info.machine_ip)
            if task:
                task_deliver=TaskDeliver(
                    run_id=task._id,
                    infer=task.type.infer,
                    fit=task.type.fit,
                )
                logger.info(f'deliver task to worker {task._id}')
                return RES(data = task_deliver)
            logger.info('no task available')
            return RES(data=None,msg='no task available')
    except Exception as e:
        return RES(code=-1, msg=f'error:{e}')

@dataclass
class SetStatus:
    run_id:str
    status:str
    token:str

@router.post('/set_task_state')
async def set_task_state(
    data:Annotated[SetStatus, Body()]
) -> RES[bool]:
    try:
        if not decrypt_and_validate(data.token,password=os.getenv("WORKER_PASSWORD","")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"fail to check worker token: {data.token}",
            )
        async with sem:
            if data.status not in ["RUNNING", "FINISHED", "FAILED", "KILLED", "SCHEDULED"]:
                return RES(code=-1, msg=f'error:{data.status} not in ["RUNNING", "FINISHED", "FAILED", "KILLED", "SCHEDULED"]')
            data_status = cast(Literal["RUNNING", "FINISHED", "FAILED", "KILLED", "SCHEDULED"], data.status)
            task = await OP.set_status(data.run_id, data_status)
            if task:
                return RES(data = True)
            return RES(data=None,msg=f'fail to set task: {data.run_id}')
    except Exception as e:
        return RES(code=-1, msg=f'error:{e}')