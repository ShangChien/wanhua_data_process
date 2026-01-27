import uvicorn
import os
import signal
import asyncio
from fastapi import FastAPI,Request,Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from .utils import RES,on_create,on_destroy,worker_func, worker_state
from typing import Any

@asynccontextmanager
async def lifespan(app: FastAPI):
	# on_startup event
	await on_create(app)

	yield
	# on_shutdown event
	await on_destroy(app)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/state")
async def get_state(req:Request)->RES[Any]:
	try:
		shared_pid_dict= req.app.state.shared_pid_dict
		data={
			'pid_dict': shared_pid_dict,
			'queue': req.app.state.queue.qsize(),
			'task_tobe_cancel': worker_state.tasks_tobe_cancel,
			'task_done': worker_state.tasks_done,
			'main_pid': os.getpid(),
			'version': '0.0.1',
		}
		print('worker state:',data)
		return RES(data=data)
	except Exception as e:
		return RES(code=-1,msg=f'worker state error: {e}')

class RunId(BaseModel):
	id:str

@app.post('/stop_current_task')
async def kill_task_by_id(req: Request, data:RunId=Body())->RES[str]:
	try:
		pid = req.app.state.shared_pid_dict.get(data.id)
		if pid:
			# 先取消并重启 worker
			print('停止之前的worker')
			for _worker in req.app.state.workers:
				_worker.cancel()

			# 停止任务进程
			os.kill(pid, signal.SIGKILL)
			print(f"Task with id:{data.id}, pid:{pid} stopped")

			# 创建新的worker
			print('创建新的worker')
			req.app.state.workers = [
                asyncio.create_task(worker_func( req.app.state.shared_pid_dict))
            ]
			
			return RES(data=f"worker task with id:{data.id}, pid:{pid} stopped")
		else:
			print(f"worker no task found with id {data.id}")
			return RES(code=-1,msg=f"worker no task found with id {data.id}")
	except Exception as e:
		return RES(code=-1,msg=f'worker kill task error: {e}')


if __name__ == "__main__":
  uvicorn.run(app="service.main:app",
			  host="0.0.0.0",
			  port=5001,)