import os
from typing import Literal, Any, TypeVar, Generic, Optional,cast
from pydantic import BaseModel
import httpx,logging
from motor.motor_asyncio import AsyncIOMotorCollection
from ..db.utils import DB,AsyncIOMotorDatabase

MODELS_DIR = '/vepfs/fs_users/chensq/project/data_uniqsar/models'
FILES_DIR = '/vepfs/fs_users/chensq/project/data_uniqsar/files'

logger = logging.getLogger("app")

qsarDB: AsyncIOMotorDatabase = cast(AsyncIOMotorDatabase, DB.db)
user_collection: AsyncIOMotorCollection  = qsarDB['user']
task_collection: AsyncIOMotorCollection  = qsarDB['task']

T = TypeVar('T')
class RES(BaseModel, Generic[T]):
	code: int = 0
	data: T | None = None
	msg: str = ''

	class Config:
		arbitrary_types_allowed = True

class InitSetting(BaseModel):
	solution: Literal['drugs', 'polymers'] | None = None
	config_path: str | dict[str, Any] | None = None
	model_dir: str | None = None
	seed: int | None = 42

class TaskInfo(BaseModel):
	name: str
	ctime: float
	run_id:str
	type: Literal['fit', 'infer']
	experiment_name:str|None=None
	experiment_id:str|None=None
	

class FitConfig(BaseModel):
	task: Literal['classification', 'regression', 'multiclass',
		'multilabel_classification', 'multilabel_regression']
	data_path: str
	target_cols: list[str]
	smiles_col: str | None = None  # 当data_path为.csv时为必选参数；.sdf不需要设置
	config_path: str | None = None
	split_method: Literal['random', 'scaffold', 'group', 'stratified'] = 'random'
	hpo_enable: bool | None = False
	group_col: str | None = None

class InferConfig(BaseModel):
	data_path:str #格式为.sdf或者.csv
	train_run_id: str # 获取训练完成的模型
	smiles_col:Optional[str]

class TaskData(BaseModel):
	task_info: TaskInfo
	init_cfg: InitSetting
	task_config: FitConfig | InferConfig

class InFit(BaseModel):
	name: str
	file_id: str  # 转换为data_path
	config_dict: dict
	hpo_enable: bool | None = False

class Fit(InFit):
	run_id: str

class InInfer(BaseModel):
	name: str
	model_trained_run_id: str  # model_id -> model_dir
	file_id: str  # 转换为data_path
	explain: bool|None = False
	smiles_col: str | None = None  # 当data_path为.csv时为必选参数；.sdf不需要设置
	target_col: str | None = None

class Infer(InInfer):
	run_id:str

class TaskType(BaseModel):
	fit:InFit | None = None
	infer:InInfer | None = None

async def create_train_task_v2(train_data:Fit) -> RES[str]:
	try:
		async with httpx.AsyncClient(base_url='http://101.126.67.113:5001') as client:
			response = await client.get('/state')
			response.raise_for_status()
			res_state:dict = response.json()
			if res_state.get('code',-1) == 0:
				headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
				print(train_data.model_dump_json())
				response = await client.post('/train_v2', json=train_data.model_dump(), headers=headers)
				# 确保请求成功
				response.raise_for_status()
				res_out:dict = response.json()
				if res_out.get('code',-1)==0:
					return RES(data='ok')
				else:
					return RES(code=-1, msg=res_out.get('msg','no worker error info'))
			else:
				return RES(code=-1,msg=res_state.get('msg','no worker error info'))
	except Exception as e:
		return RES(code=-1,msg=f'submit error:{e}')

async def create_train_task(task_info: TaskInfo, init_cfg: InitSetting, fit_cfg: FitConfig) -> RES[str]:
	try:
		if init_cfg.solution is None and init_cfg.config_path is None:
			raise ValueError("Either solution or config_path must be provided.")
		if init_cfg.config_path is not None and isinstance(init_cfg.config_path, str) and not os.path.exists(init_cfg.config_path):
			raise FileNotFoundError(f"Config file not found: {init_cfg.config_path}")
		if fit_cfg.split_method in ['group', 'stratified'] and fit_cfg.group_col is None:
			raise ValueError("group_col must be provided when split_method is 'group' or 'stratified'.")

		async with httpx.AsyncClient(base_url='http://101.126.67.113:5001') as client:
			response = await client.get('/state')
			response.raise_for_status()
			res_state:dict = response.json()
			if res_state.get('code',-1) == 0:
				data = TaskData(task_info=task_info,init_cfg=init_cfg,task_config=fit_cfg)
				headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
				print(data.model_dump_json())
				response = await client.post('/train', json=data.model_dump(), headers=headers)
				# 确保请求成功
				response.raise_for_status()

				res_out:dict = response.json()
				if res_out.get('code',-1)==0:
					return RES(data='ok')
				else:
					return RES(code=-1, msg=res_out.get('msg','no worker error info'))
			else:
				return RES(code=-1,msg=res_state.get('msg','no worker error info'))
	except Exception as e:
		return RES(code=-1,msg=f'submit error:{e}')


async def create_infer_task(infer_data:Infer) -> RES[str]:
	try:
		async with httpx.AsyncClient(base_url='http://101.126.67.113:5001') as client:
			response = await client.get('/state')
			response.raise_for_status()
			res_state:dict = response.json()
			if res_state.get('code',-1) == 0:
				headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
				response = await client.post('/infer', json=infer_data.model_dump(), headers=headers)
				# 确保请求成功
				response.raise_for_status()
				res_out:dict = response.json()
				if res_out.get('code',-1)==0:
					return RES(data='ok')
				else:
					return RES(code=-1, msg=res_out.get('msg','worker error'))
			else:
				return RES(code=-1,msg=res_state.get('msg','worker error'))
	except Exception as e:
		return RES(code=-1,msg=f'submit error:{e}')


async def kill_task_by_run_run_id(run_id:str,machine_ip:str) -> RES[str]:
	try:
		async with httpx.AsyncClient(base_url=machine_ip) as client:
			response = await client.get('/state')
			response.raise_for_status()
			res_state:dict = response.json()
			if res_state.get('code',-1) == 0:
				headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
				response = await client.post('/stop_with_run_id', json={'run_id': run_id}, headers=headers)
				# 确保请求成功
				response.raise_for_status()
				res_out:dict = response.json()
				print(res_out)
				if res_out.get('code',-1)==0:
					return RES(data='ok')
				else:
					return RES(code=-1, msg=res_out.get('msg','no worker error info'))
			else:
				return RES(code=-1,msg=res_state.get('msg','no worker error info'))
	except Exception as e:
		return RES(code=-1,msg=f'error: {e}')
	
async def cancel_task(run_id:str) -> RES[str]:
	try:
		async with httpx.AsyncClient(base_url='http://101.126.67.113:5001') as client:
			response = await client.get('/state')
			response.raise_for_status()
			res_state:dict = response.json()
			if res_state.get('code',-1) == 0:
				headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
				response = await client.post('/task_cancel', json={'run_id':run_id}, headers=headers)
				# 确保请求成功
				response.raise_for_status()
				res_out:dict = response.json()
				if res_out.get('code',-1)==0:
					return RES(data='task will be cancel')
				else:
					return RES(code=-1, msg=res_out.get('msg','no worker error info'))
			else:
				return RES(code=-1,msg=res_state.get('msg','no worker error info'))
	except Exception as e:
		return RES(code=-1,msg=f'error: {e}')




