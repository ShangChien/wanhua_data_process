from .utils import RES,ChartData,MODELS_DIR,MLFLOW_EXPERIMENT_INFER
from pydantic import BaseModel
from pathlib import Path
from fastapi import APIRouter,Body,HTTPException,Depends
from fastapi.responses import FileResponse
from typing import Any,Annotated
import json,logging
from ...user.utils import verify_jwt_token

logger = logging.getLogger("app")

router = APIRouter(
    prefix="/chart",
    tags=["chart"],
)

class DataIn(BaseModel):
    run_id:str

@router.post('/all_info', dependencies=[Depends(verify_jwt_token)])
async def get_total_info(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_all_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')
    
@router.post('/tsne', dependencies=[Depends(verify_jwt_token)])
async def get_tsne(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_tsne_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')

@router.post('/metrics', dependencies=[Depends(verify_jwt_token)])
async def get_metrics(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_metrics_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')

@router.post('/predict', dependencies=[Depends(verify_jwt_token)])
async def get_predict(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_predict_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')

@router.post('/distribution', dependencies=[Depends(verify_jwt_token)])
async def get_distribution(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_distribution_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')
    
@router.post('/params', dependencies=[Depends(verify_jwt_token)])
async def get_params(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_params_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')

@router.post('/all_model_details', dependencies=[Depends(verify_jwt_token)])
async def get_models(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        chart = ChartData(data.run_id)
        await chart.async_init()
        data_out=chart.get_all_details_json()
        return RES(data=data_out)
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')
    
@router.post('/predict_table_data', dependencies=[Depends(verify_jwt_token)])
async def predict_table_data(data: Annotated[DataIn, Body()]) -> RES[Any]:
    try:
        json_file = Path(MODELS_DIR, MLFLOW_EXPERIMENT_INFER, data.run_id,'ChartDataInfer/result.json')
        if json_file.exists():
            with open(json_file, "r") as f:
                data_raw:dict = json.load(f)
                for key in data_raw:
                    item:dict[str,Any]=data_raw[key]
                    for attr in item:
                        if attr.startswith('2D_Graph'):
                            name_frags = data_raw[key][attr].split('/')
                            data_raw[key][attr] = '->'.join([name_frags[-5], name_frags[-2], name_frags[-1]]) #eg: "677d516512174f6ba657f0e5fc987e46->adme-fang-PERM-1->plot2D_101.png"
                return RES(data=list(data_raw.values()))
        else:
            return RES(code=-1, msg='error: json_file not found')
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')

@router.get('/predict_image/{image_name}')
async def get_image(image_name: str):# -> FileResponse | RES[Any]:
    try:
        name_frags=image_name.split('->')
        # 检查文件是否存在
        if len(name_frags)!= 3 :
            raise HTTPException(status_code=400, detail="image文件命名应该为: **->**->**.png")
        image_path = Path(MODELS_DIR, MLFLOW_EXPERIMENT_INFER, name_frags[0], 'ChartDataInfer/plot', name_frags[1], name_frags[2])
        # 检查文件是否存在
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="image未找到")
        return FileResponse(
            path=image_path,
            media_type="image/png"
        )
    except Exception as e:
        return RES(code=-1, msg=f'error: {e}')