from fastapi import APIRouter, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal
from pathlib import Path
from ..user.utils import verify_jwt_token
from .utils import RES,FileUploadRes, get_uid, run_check_multi, save_df_to_file, save_upload_file, get_task_type
import logging

logger = logging.getLogger("app")

router = APIRouter(
    prefix="/file",
    tags=["file"],
    dependencies=[Depends(verify_jwt_token)]
)

# raw_files, vaild_files
FILES_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/files" 

@router.post("/upload")
async def create_file(file: UploadFile) -> RES[FileUploadRes]:
    file_content: bytes = await file.read()
    file_name=file.filename
    file_extension: str = file_name.split(".")[-1].lower() if file_name else ""
    uid: str = get_uid()
    print(f"files name: {file_name}; raw name: {file.filename}")

    supported_extension = ["csv", "sdf"]
    if file_extension not in supported_extension:
        return RES(code=-1, msg="不支持该文件类型")
    
    try:
        file_path = Path(FILES_DIR,"raw_files", f"{uid}_raw_{file_name}")
        columns = save_upload_file(path=file_path, content=file_content)
        return RES(data=FileUploadRes(columns=columns, size=len(file_content), file_id=uid))
    except Exception as e:
        return RES(code=-1, msg=f"{str(e)}")

class fileCheck(BaseModel):
    file_id: str
    smiles_col: str
    target_cols: list[str]

@router.post("/check")
async def check_file(data: fileCheck) -> RES[dict]:
    try:
        files = list(Path(FILES_DIR, "raw_files").glob(pattern=f"{data.file_id}_*"))
        if len(files) == 1:
            with open(files[0], "rb") as f:
                file_content = f.read()
                file_type: Literal[".csv", ".sdf"] = (
                    ".csv" if files[0].name.endswith("csv") else ".sdf"
                )
                res_check = run_check_multi(
                    data_bytes=file_content,
                    type=file_type,
                    smiles_col=data.smiles_col,
                    target_cols=data.target_cols,
                )

                ## 猜测任务类型
                guess_task_type = ''
                try:
                    guess_task_type=get_task_type(res_check['data_df'], data.target_cols)
                except Exception as e:
                    logger.error(f'猜测任务类型失败: {e}; file_id: {data.file_id}')
                ## save new df
                uid = get_uid()
                _base_name="_".join(files[0].name.split('_')[2:])
                file_path=Path(FILES_DIR, 'valid_files', f'{uid}_valid_{_base_name}')
                save_df_to_file(
                    new_df = res_check['data_df'],
                    file_type = file_type,
                    out_path= file_path
                )

                if len(res_check["error_rows"]) > 0:
                    return RES(
                        data = {
                            "error_rows": res_check['error_rows'],
                            "file_id":uid,
                            "guess_task_type":guess_task_type
                        }
                    )
                else:
                    return RES(data={
                        'file_id':uid,
                        "guess_task_type":guess_task_type
                    })
        else:
            return RES(code=-1, msg=f"file no found: {data.file_id}")
    except Exception as e:
        return RES(code=-1, msg=f"error:{e}")

@router.post("/upload_infer_file")
async def create_infer_file(file: UploadFile) -> RES[FileUploadRes]:
    file_content: bytes = await file.read()
    file_name=file.filename
    file_extension: str = file_name.split(".")[-1].lower() if file_name else ""
    uid: str = get_uid()
    print(f"files name: {file_name}; raw name: {file.filename}")

    supported_extension = ["csv", "sdf"]
    if file_extension not in supported_extension:
        return RES(code=-1, msg="不支持该文件类型")
    
    try:
        file_path = Path(FILES_DIR,"raw_files", f"{uid}_raw_infer_{file_name}")
        columns = save_upload_file(path=file_path, content=file_content)
        return RES(data=FileUploadRes(columns=columns, size=len(file_content), file_id=uid))
    except Exception as e:
        return RES(code=-1, msg=f"{str(e)}")

class InferFileCheck(BaseModel):
    file_id: str
    smiles_col: str|None = 'SMILES'
    target_cols: list[str]|None = None

@router.post("/check_infer_file")
async def check_infer_file(data: InferFileCheck) -> RES[dict]:
    try:
        files = list(Path(FILES_DIR, "raw_files").glob(pattern=f"{data.file_id}_*"))
        if len(files) == 1:
            with open(files[0], "rb") as f:
                file_content = f.read()
                file_type: Literal[".csv", ".sdf"] = (
                    ".csv" if files[0].name.endswith("csv") else ".sdf"
                )
                res_check = run_check_multi(
                    data_bytes=file_content,
                    type=file_type,
                    smiles_col= data.smiles_col if data.smiles_col else 'SMILES' ,
                    target_cols=data.target_cols,
                )
                ## save new df
                uid = get_uid()
                _base_name="_".join(files[0].name.split('_')[2:])
                file_path=Path(FILES_DIR, 'valid_files', f'{uid}_valid_infer_{_base_name}')
                save_df_to_file(
                    new_df = res_check['data_df'],
                    file_type = file_type,
                    out_path= file_path
                )

                if len(res_check["error_rows"]) > 0:
                    return RES(
                        data = {"error_rows": res_check['error_rows'],'file_id':uid}
                    )
                else:
                    return RES(data={
                        'file_id':uid
                    })
        else:
            return RES(code=-1, msg=f"file no found: {data.file_id}")
    except Exception as e:
        return RES(code=-1, msg=f"error:{e}")


@router.get('/download_template')
async def download() -> FileResponse:

    # 使用Path来获取当前执行文件的目录
    file_path= Path('/vepfs/fs_users/chensq/project/data_uniqsar/files/assets/template.csv')
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件未找到")
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type='text/csv',
        headers={"Content-Disposition": f"attachment; filename={file_path.name}"}
    )