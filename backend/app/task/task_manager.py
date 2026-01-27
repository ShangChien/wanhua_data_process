from datetime import datetime
from dataclasses import dataclass,field,asdict
from pathlib import Path
from typing import  Any, Literal, cast
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult, UpdateResult
from .utils import RES,InInfer,InFit,TaskType
import re, logging
import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorCollection
from ..db.utils import DB,AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger("app")

semaphore = asyncio.Semaphore(1)


RUNTIME_DATA_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/runtime_data"
MODELS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/models"

qsarDB: AsyncIOMotorDatabase = cast(AsyncIOMotorDatabase, DB.db)
user_collection: AsyncIOMotorCollection  = qsarDB['user']
task_collection: AsyncIOMotorCollection  = qsarDB['task']

@dataclass
class Task:
	name:str
	owner:str
	type:TaskType
	model_task:Literal['classification', 'regression', 'multilabel_classification', 'multilabel_regression', 'multiclass']
	data_path:Path
	machine_ip:str=''
	status:Literal["RUNNING","FINISHED","FAILED","KILLED","SCHEDULED"] = 'SCHEDULED' 
	exec_time:float|None = None
	end_time:float|None = None
	remove_flag:bool = False
	config_dict:dict = field(default_factory= lambda: dict())
	metrics:dict = field(default_factory= lambda: dict())
	params:dict = field(default_factory= lambda: dict())
	create_time: float = field(default_factory= lambda: datetime.now().timestamp())

	def to_dict(self) -> dict:
		task_dict = asdict(self)
		task_dict['data_path'] = self.data_path.as_posix()  # Convert Path to string
		task_dict['type'] = self.type.model_dump()
		return task_dict
	
	async def write2DB(self) -> RES[InsertOneResult]:
		res:InsertOneResult = await task_collection.insert_one(self.to_dict())
		logger.info(f"insert task to DB: {res.inserted_id}")
		return RES(data=res)

@dataclass
class TaskInDB(Task):
	_id:str=''

	@staticmethod
	def db_raw2Task(data:dict) -> dict[Any, Any]:
		data['_id'] = str(data['_id'])
		data['data_path'] = Path(data['data_path'])
		data['type'] = TaskType(
			fit = InFit(**data['type']['fit']) if data['type']['fit'] else None,
			infer = InInfer(**data['type']['infer']) if data['type']['infer'] else None,
		)
		return data

@dataclass
class DB_Operation:
	@classmethod
	async def commit_task(cls,task:Task) -> str|None:
		res = await task_collection.insert_one(task.to_dict())
		if res and res.acknowledged:
			return str(res.inserted_id)

	@classmethod
	async def get_task_info(cls,run_id:str) -> TaskInDB | None:
		## await cls.refresh_status(run_id)
		res:dict|None = await task_collection.find_one({"_id":ObjectId(run_id)})
		if res:
			return TaskInDB(**TaskInDB.db_raw2Task(res))

	@classmethod
	async def set_status(cls, run_id:str, status:Literal["RUNNING","FINISHED","FAILED","KILLED","SCHEDULED"]) -> dict|None:
		res_old= await task_collection.find_one_and_update(
			{"_id":ObjectId(run_id)},
			{"$set":{'status':status}},
			return_document=ReturnDocument.BEFORE
		)
		if res_old is None:
			logger.error(f'fail set task state, not found task: {run_id}')
			return None
		if res_old['status'] == "RUNNING":
			await cls.refresh_status(run_id)
		res_old['status']=status
		logger.info(f'set task {run_id} status {status}')
		return res_old

	@classmethod
	async def refresh_status(cls, run_id:str) -> Any | None:
		task=await cls.get_task_info(run_id)
		if not task:
			return RES(code=-1,msg=f'no run_id task: {run_id}')
		
		sub_dir= "783693552791073446" if task.type.fit else "639031919007598614"
		log_file_path = Path(MODELS_DIR, sub_dir, run_id, 'qsar_runtime.log')
		if not log_file_path.exists():
			logger.error(f"no found filename start with({run_id})")
			return
		time_dict=extract_exec_end_times(log_file_path)
		logger.info(f'获取任务{run_id}的运行时间{time_dict}')
		res= await task_collection.find_one_and_update(
			{"_id":ObjectId(run_id)},
			{"$set":{
				'exec_time':time_dict['exec_time'],
				"end_time":time_dict['end_time']}
			},
			return_document=ReturnDocument.AFTER
		)
		logger.info(f'refresh task {run_id} time status')
		return res

	@classmethod
	async def stop(cls,run_id:str) -> RES[bool]:
		task = await cls.get_task_info(run_id)
		if not task:
			return RES(code=-1,msg="DB search task error")

		if task.status not in ['RUNNING', 'SCHEDULED']:
			return RES(code=-1,msg=f"task run_run_id: {run_id} status is {task.status}, which not in ['RUNNING', 'SCHEDULED']")

		# 如果任务在计划中，直接标记数据库状态
		# if task.status == "SCHEDULED":
		res_set = await cls.set_status(run_id,'KILLED')
		if res_set:
			return RES(data=True, msg=f'success stop task {run_id}, and set status "SCHEDULED" to "KILLED"')
		return RES(code=-1,msg=f'current state: "SCHEDULED"; fail to set status "KILLED " task {run_id}')

		## if task.status == "RUNNING":
		## 如果正在运行中，向worker发起命令请求停止
		res: RES[str] = await kill_remote_task_by_run_id(run_id,task.machine_ip)
		if res.code != 0:
			return RES(code=-1, msg=f'error: {res.msg}')

		res_set = await cls.set_status(run_id,'KILLED')
		if res_set:
			return RES(data=True, msg=f'success stop task {run_id}, and set status "RUNNING" to "KILLED "')
		return RES(code=-1,msg=f'current state: "RUNNING"; fail to set status "KILLED" task {run_id}')

	@classmethod
	async def rm_task(cls, run_id:str)-> RES[bool]:
		task = await cls.get_task_info(run_id)
		if task:
			if task.remove_flag:
				return RES(data=True)
			logger.info(task.to_dict())
			res = await task_collection.update_one(
				{"_id": ObjectId(run_id)},
				{"$set": {"remove_flag":True}}
			)
			logger.info(f'已删除{res}')
			if res and res.acknowledged:
				return RES(data=True,msg="remove task ok")
			return RES(code=-1,msg="DB update remove task error")
		else:
			return RES(code=-1,msg="DB search task error")

	@classmethod
	async def get_task_list_info(cls, username:str) -> list[dict[str, Any]]:
		# 返回每个任务的uid, name，创建时间，状态，
		cursor = task_collection.find({'owner':username})
		task_list = [TaskInDB(**TaskInDB.db_raw2Task(task)) async for task in cursor if not task['remove_flag']]
		tasks_info= []
		logger.info(f"{username}'s total {len(task_list)} tasks found")
		for task in task_list:
			## 刷新时间
			logger.info(f'task: {task}')
			if task.status=="RUNNING":
				res=await cls.refresh_status(task._id)
				
				if res:
					res_data = TaskInDB(**TaskInDB.db_raw2Task(res))
					task.exec_time = res_data.exec_time
					task.end_time = res_data.end_time
			logger.info(f'task: {task}')
			task_type_infer=task.type.model_dump()['infer']
			task_out={
				'run_id': task._id,
				'name': task.name,
				'ctime':task.create_time,
				'model_task':task.model_task,
				"data_path":task.data_path.name,
				'task_type':'fit' if task.type.fit else 'infer',
				'state':task.status,
				"model_trained_run_id": task_type_infer['model_trained_run_id'] if task_type_infer  else ''
			}
			logger.info(f'task_out: {task_out}')
			tasks_info.append(task_out)
		return tasks_info

	@classmethod
	async def clear(cls, username:str) -> UpdateResult:
		res = await task_collection.update_many(
			{'owner':username},
			{'$set':{'remove_flag':True}}
		)
		return res

	@classmethod
	async def deliver_task(cls, machine_ip:str)->TaskInDB|None:
		res=await task_collection.find_one_and_update(
			{"status": "SCHEDULED","remove_flag":False},
			{"$set": { 
				"status": "RUNNING",
				"machine_ip":machine_ip
			}},
			return_document=ReturnDocument.BEFORE
		)
		if res:
			return TaskInDB(**TaskInDB.db_raw2Task(res))


async def kill_remote_task_by_run_id(run_id:str,machine_ip:str) -> RES[str]:
	try:
		async with httpx.AsyncClient(base_url=f"http://{machine_ip}") as client:
			response = await client.get('/state')
			response.raise_for_status()
			res_state:dict = response.json()
			if res_state.get('code',-1) == 0:
				headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
				response = await client.post('/stop_current_task', json={'run_id': run_id}, headers=headers)
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

def extract_exec_end_times(log_file_path: Path) -> dict[str, float | None]:
	time_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \|')
	
	exec_time = None
	end_time = None
	
	with open(log_file_path, 'r', encoding='utf-8') as file:
		# Find the start time (first occurrence)
		for line in file:
			time_match = time_pattern.search(line)
			if time_match:
				exec_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S').timestamp()
				break
		
		# Find the end time (last occurrence)
		file.seek(0, 2)  # Go to the end of the file
		pos = file.tell()
		while pos > 0 and end_time is None:
			pos -= 1
			file.seek(pos)
			char = file.read(1)
			if char == '\n':
				line = file.readline()
				time_match = time_pattern.search(line)
				if time_match:
					end_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S').timestamp()

	return {"exec_time": exec_time, "end_time": end_time}

def monitor_log_file_progress(log_file_path: Path, nn_count:int, ml_count:int, n_fold:int,explain:bool|None=None) -> float:
	### explain 
	# None: train task
	# False: predict task without explain
	# True: predict task with explain

	total_fold_count = (nn_count + ml_count) * n_fold
	if explain:
		total_fold_count=total_fold_count * 2
	finished_fold_count = 0

	## 正则匹配到的fold个数, 如果匹配到"Predict done" or "Train done"直接return 1.0
	fold_pattern = re.compile(r"fold (\d+), result")
	predict_done_pattern= re.compile(r"Predict done")
	train_done_pattern= re.compile(r"Train done")
	with open(log_file_path, 'r', encoding='utf-8') as file:
		# 如果开启explain,第一次匹配到Predict done,flag改为True,第二次直接return1.0"
		flag_explain_return_predict_done = True if explain else False
		for line in file:
			fold_match = fold_pattern.search(line)
			if fold_match:
				finished_fold_count = finished_fold_count + 1
			else:
				if explain:
					predict_match = predict_done_pattern.search(line)
					if predict_match:
						if flag_explain_return_predict_done:
							return 1.0
						else:
							flag_explain_return_predict_done = True
				else:
					predict_match = predict_done_pattern.search(line)
					train_match = train_done_pattern.search(line)
					if train_match or predict_match:
						return 1.0
				
	progress_percent= finished_fold_count/total_fold_count
	return progress_percent

