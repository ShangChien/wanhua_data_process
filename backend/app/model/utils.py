from typing import TypeVar, Generic, cast, Any
from pydantic import BaseModel
import logging
from pathlib import Path
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorCollection
from ..db.utils import DB,AsyncIOMotorDatabase
from ..task.task_manager import Task,TaskType,InInfer,InFit, DB_Operation as OP

logger = logging.getLogger("app")

# raw_files, vaild_files
EXPERIMENT_NAME = "my_experiment"
MODELS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/models"
MLRESULTS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/mlruns"
FILES_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/files"

qsarDB: AsyncIOMotorDatabase = cast(AsyncIOMotorDatabase, DB.db)
user_collection: AsyncIOMotorCollection  = qsarDB['user']
task_collection: AsyncIOMotorCollection  = qsarDB['task']

T = TypeVar("T")
class RES(BaseModel, Generic[T]):
	code: int = 0
	data: T | None = None
	msg: str = ""

@dataclass
class TaskOut(Task):
	run_id:str=''
	@staticmethod
	def db_raw2Task(data:dict) -> dict[Any, Any]:
		## 适配返回的类型
		data['run_id'] = str(data.pop('_id'))

		data['data_path']=Path(data['data_path'])
		data['type']=TaskType(
			fit=InFit(**data['type']['fit']) if data['type']['fit'] else None,
			infer=InInfer(**data['type']['infer']) if data['type']['infer'] else None,
		)
		return data

async def available_models(username:str) -> list[TaskOut]:
	# models:list[TaskOut]=[]
	cursor = task_collection.find({
		'owner':username,
		'type.infer': {'$ne': None},
		'status':'FINISHED',
		'remove_flag':False
	})
	task_list = [
		TaskOut(**TaskOut.db_raw2Task(task)) 
		async for task in cursor
	]
	return task_list


