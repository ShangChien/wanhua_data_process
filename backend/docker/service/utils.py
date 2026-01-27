import asyncio
import concurrent.futures
from multiprocessing import Manager
import os,yaml
from dataclasses import dataclass,field
from typing import Literal, Any, TypeVar, Generic, Optional, Union, Dict, Set
from pydantic import BaseModel
from fastapi import FastAPI
from .utils_predict import Draw2DMol, ChartDataInfer
from .deliver_token_utils import encrypt_timestamp
import httpx
from pathlib import Path

deploy_mode = os.getenv('DEPLOY_MODE','dev')

ARTIFACT_NAME = "my_model"
EXPERIMENT_Fit = "my_experiment_fit"
EXPERIMENT_Infer = "my_experiment_infer"
MODELS_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/models"
FILES_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/files"

T = TypeVar("T")

class RES(BaseModel, Generic[T]):
	code: int = 0
	data: Optional[T] = None
	msg: str = ""

class Fit(BaseModel):
	name: str
	run_id: str
	file_id: str  # 转换为data_path
	config_dict: Dict 
	hpo_enable: Optional[bool]  = False

class Infer(BaseModel):
	run_id:str
	name: str
	model_trained_run_id: str  # model_id -> model_dir
	file_id: str  # 转换为data_path
	explain: Optional[bool] = False
	smiles_col: Optional[str] = None  # 当data_path为.csv时为必选参数；.sdf不需要设置
	target_col: Optional[str] = None

# 递归更新字典
def update_yaml_dict(yaml_path, update_data):
	with open(yaml_path, 'r') as file:
		data = yaml.safe_load(file)

	# 递归更新字典
	def recursive_update(d, u):
		for k, v in u.items():
			if isinstance(v, dict) and k in d and isinstance(d[k], dict):
				recursive_update(d[k], v)
			else:
				d[k] = v
	recursive_update(data, update_data)
	return data  

def train(train_data:Fit):
	try:
		from qsar import UniProp  # type: ignore
		print(f"inner process start:{train_data.name}")
		model_dir = f"{MODELS_DIR}/783693552791073446/{train_data.run_id}"
		print(f"process new task:{train_data.run_id}")
		## 获取train input file
		files = list(Path(FILES_DIR, "valid_files").glob(pattern=f"{train_data.file_id}_*"))
		if len(files)==1:
			input_data = files[0]
		else:
			if len(files)>1:
				raise FileExistsError(f'multi input train files found, file_id: {train_data.file_id}')
			else:
				raise FileNotFoundError(f'input train files not found, file_id: {train_data.file_id}')
		
		## 改写cfg_dict
		config=update_yaml_dict(Path(Path(__file__).parent, 'config_default.yaml'),train_data.config_dict)
		if input_data.suffix=='.sdf':
			config['Datahub']['smiles_col'] = 'SMILES'
		print('config_dict_parse:', config)
		print('config_dict_raw:', train_data.config_dict)

		## UniProp init
		model = UniProp(
			config_path = config,
			log_path = f"{model_dir}/qsar_runtime.log"
		)
		config = model.config
		print("after UniProp init")

		print("before fit")
		model.fit(
			data_path=input_data.as_posix(),
			out_dir=model_dir,
			hpo_enable=train_data.hpo_enable,
		)
		model_path = model.model_dir
		print(f'UniProp model path: {model_path}')
		set_task_status(train_data.run_id,'FINISHED')
	except Exception as e:
		print(f"task process error: {e}")
		set_task_status(train_data.run_id,'FAILED')
		raise e
	
def infer(infer_data:Infer):
	try:
		from qsar import UniProp  # type: ignore
		print(f"inner process infer start:{infer_data.name}")
		model_dir = f"{MODELS_DIR}/783693552791073446/{infer_data.model_trained_run_id}"
		output_dir  = f"{MODELS_DIR}/639031919007598614/{infer_data.run_id}"
		print(f"process new infer task:{infer_data.run_id}")
		print(infer_data)
		model = UniProp(
			model_dir=model_dir,
			log_path = f"{output_dir}/qsar_runtime.log"
		)
		print("after UniProp init")
		## 获取infer input file
		files = list(Path(FILES_DIR, "valid_files").glob(pattern=f"{infer_data.file_id}_*"))
		if len(files)==1:
			input_data = files[0]
		else:
			if len(files)>1:
				raise FileExistsError(f'multi input train files found, file_id: {infer_data.file_id}')
			else:
				raise FileNotFoundError(f'input train files not found, file_id: {infer_data.file_id}')
		print("新建模型预测输出文件")
		
		print(f"before infer, input_file:{input_data.as_posix()},exist:{input_data.exists()}",)
		out = model.predict(
			data_path=input_data.as_posix(),
			out_dir=os.path.join(output_dir, 'Predict'),
			smiles_col=infer_data.smiles_col,
		)
		set_task_status(infer_data.run_id,'FINISHED')
		print(f'infer finished:{out}')
	except Exception as e:
		print(f"task process error: {e}")
		set_task_status(infer_data.run_id,'FAILED')
		raise e
	
	try:
		input_basename = Path(input_data).stem 
		data_path = os.path.join(output_dir, 'Predict', f"{input_basename}.predict_0.csv")
		config_path = os.path.join(model_dir, "config.yaml")
		chart_save_path = os.path.join(output_dir, 'ChartDataInfer')
		plot_save_path = os.path.join(output_dir, 'ChartDataInfer', 'plot') if infer_data.explain else None
		print('Start init chart')
		chart_data = ChartDataInfer(
			data_path, 
			config_path,
			chart_save_path,
			smiles_col=infer_data.smiles_col,
			)
		print('Get result')
		chart_data.get_result(explain_dir=plot_save_path)

		if infer_data.explain:
			print('Start get explain')
			model.explain(
				data_path=input_data.as_posix(),
				out_dir=os.path.join(output_dir, 'Explain'),
				smiles_col=infer_data.smiles_col,
			)
			print('Start Draw2DMol')
			draw2d = Draw2DMol(
				os.path.join(output_dir, 'Explain'),
				config_path,
				plot_save_path
				)
			draw2d.get_all_drawer()
	except Exception as e:
		print(f"task process explain chart error: {e}")
	
	

@dataclass
class Task:
	task_param: Union[Infer,Fit]
	shared_pid_dict:Any

@dataclass
class WorkerState:
	tasks_tobe_cancel:Set = field(default_factory=set)
	tasks_done:Set = field(default_factory=set)

worker_state=WorkerState()

def run_task_with_inner_set_pid(task:Task):
	try:
		run_id=task.task_param.run_id
		task.shared_pid_dict[run_id] = os.getpid() # Set the shared PID
		print('get inner pid:',task.shared_pid_dict[run_id])
		if isinstance(task.task_param, Fit):
			print('run train_v2()...')
			param:Fit = task.task_param
			train(param)
		if isinstance(task.task_param, Infer):
			print('run infer()...')
			infer(task.task_param)
	except Exception as e:
		print(f"Error in run_task_with_inner_set_pid: {e}")
		raise e
	finally:
		_pid = task.shared_pid_dict.pop(run_id, None)
		print(f"run_task_with_inner_set_pid内部删除shared_pid_dict中的id: {_pid}")
	

async def worker_func(shared_pid_dict):
	loop = asyncio.get_event_loop()
	run_id:str=''  
	try:
		while True:
			try:
				print("等待任务")
				task_dict = acquire_task()
				if not task_dict:
					print('没有任务等待30s')
					await asyncio.sleep(30)
					continue
				print('拿到队里中的任务')
				run_id=task_dict['run_id']
				if task_dict['fit']:
					task=Fit(**task_dict['fit'],run_id=run_id)
				else:
					task=Infer(**task_dict['infer'],run_id=run_id)
				task = Task(task_param=task, shared_pid_dict=shared_pid_dict)
				print(f"开始处理任务{run_id}")
				# await asyncio.to_thread(process, task) ##python >= 3.9
				with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
					await loop.run_in_executor(executor, run_task_with_inner_set_pid, task)
				worker_state.tasks_done.add(run_id)
				## 发起请求改变状态
				# set_task_status(run_id,'FINISHED')
			except Exception as e:
				try:
					## 发起请求改变状态
					# set_task_status(run_id,"FAILED")
					print(f'worker 内部 error: {e}')
				except Exception as e:
					print(f'fail to set status:{e}')	
			finally:
				print(f'while循环内部执行任务, {run_id}')

	except asyncio.CancelledError:
		print("worker被主进程cancel")
	except Exception as e:
		print(f"worker内部任务执行时出错: {e}")
	finally:
		_pid = shared_pid_dict.pop(run_id, None)  # Ensure the shared PID is removed
		print(f"删除shared_pid_dict中的run_id: {_pid}")
		print("worker内部任务处理完毕")

def acquire_task() -> Union[Dict, None]:
	token=encrypt_timestamp('uni_qsar')
	machine_ip = f"101.126.67.113:{'5001' if deploy_mode == 'dev' else '5002' }" 
	try:
		res = httpx.post(
			url=f"http://101.126.67.113:{'7890' if deploy_mode == 'dev' else '7891' }/task/acquire_task",
			json={"token":token,"machine_ip": machine_ip}
		)
		res.raise_for_status()
		res_data = res.json()
		if res_data['code'] != 0 or not res_data['data']:
			print(f"请求任务出错: {res_data['msg']}")
			return None
		print(f"已得到任务: {res_data['data']}")
		return res_data['data']
	except Exception as e:
		print(f'请求任务出错: {e}')
		return None
	
def set_task_status(
	run_id:str,
	status:Literal["RUNNING", "FINISHED", "FAILED", "KILLED", "SCHEDULED"]
) -> Union[Dict, None]:
	token=encrypt_timestamp('uni_qsar')
	try:
		res = httpx.post(
			url=f"http://101.126.67.113:{'7890' if deploy_mode == 'dev' else '7891' }/task/set_task_state",
			json={ "run_id":run_id, "status": status, "token":token }
		)
		res.raise_for_status()
		res_data = res.json()
		if res_data['code'] != 0 or not res_data['data']:
			print(f"run_id: {run_id}, 设置任务状态出错: {res_data['msg']}")
			return None
		print(f"run_id: {run_id}, 成功设置任务状态: {status}")
		return res_data['data']
	except Exception as e:
		print(f'run_id: {run_id}, 设置任务状态出错: {e}')
		return None
	

manager = Manager()
shared_pid_dict = manager.dict()

async def on_create(app: FastAPI):
	# 程序启动时执行的钩子函数
	print("初始化")
	
	# 程序启动之后会创建worker
	app.state.workers = [asyncio.create_task(worker_func(shared_pid_dict))]
	print("创建worker")


async def on_destroy(app: FastAPI):
	# 程序结束时执行的钩子函数
	workers = app.state.workers
	
	print("等待尚未完成的任务执行完毕")
	try:
		# 等待所有繁忙的任务完成
		# 10 秒内未完成，那么程序直接结束，不再等待
		await asyncio.wait_for(asyncio.gather(*workers), timeout=10)
		pass
	except asyncio.TimeoutError:
		print("程序结束, 但还有任务尚未完成")
	finally:
		[worker.cancel() for worker in workers]
