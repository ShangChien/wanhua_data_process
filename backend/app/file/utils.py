from io import BytesIO
import pandas as pd
from pandas import DataFrame
from rdkit import Chem
import hashlib,os,re
from multiprocessing import Pool
import warnings
import uuid
from rdkit import RDLogger
import tempfile
from typing import Any, TypeVar, Generic, TypeGuard,Literal
from pydantic import BaseModel
from numpy import ndarray
from pathlib import Path
from rdkit.Chem import PandasTools
import logging

logger = logging.getLogger("app")

RDLogger.DisableLog('rdApp.*')   # type: ignore
warnings.filterwarnings("ignore")

T = TypeVar('T')
class RES(BaseModel, Generic[T]):
    code: int = 0
    data: T | None = None
    msg: str = ''

class FileUploadRes(BaseModel):
    columns:list[str]
    size:int
    file_id:str

class FileType(BaseModel):
    file_id:str
    name:str
    content:bytes
    
def get_hash_id(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def get_uid() -> str:
    return str(uuid.uuid4())

def is_ndarray(val: Any) -> TypeGuard[ndarray]:
    return isinstance(val, ndarray)


def smiles_is_valid(smiles) -> bool:
    try:
        mol: Chem.Mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return True
        else:
            return False
    except Exception as _e:
        return False

def sdf_is_valid(content: bytes) -> bool | list[int]:
    # 创建一个临时文件，并确保之后会删除它
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
        # 使用 Chem.SDMolSupplier 读取临时文件
        supplier = Chem.MultithreadedSDMolSupplier(temp_file_path, numWriterThreads=8)
        # 将供应商的内容转换为列表，以便多次遍历
        mol_list = list(supplier)
        
        # 检查是否所有分子都有效
        is_valid = all(mol is not None for mol in mol_list)
        if is_valid:
            return True
        else:
            # 获取所有 None 值的索引
            none_indices: list[int] = [index for index, mol in enumerate(mol_list) if mol is None]
        
            # 打印 None 值的索引
            print("Indices of None values:", none_indices)
        
            return none_indices

def check_smiles(smi):
    if Chem.MolFromSmiles(smi) is None:
        return False
    return True

def can_convert_to_float(element):
    try:
        float(element)
        return True
    except Exception as _e:
        return False

def check_elements_can_convert_to_float(df, target_cols:str|list[str]):
    if isinstance(target_cols, str):
        target_cols = [col.strip() for col in target_cols.split(',')]
    result = df[target_cols].applymap(can_convert_to_float)
    return result

def tmp_read_input(data_bytes:bytes,file_type:Literal['.sdf','.csv']) -> DataFrame:
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        temp_file.write(data_bytes)
        temp_file.flush()
        temp_file.seek(0)
        if file_type=='.csv':
            print('暂存临时文件：',temp_file.name)
            data: DataFrame = pd.read_csv(temp_file.name)
            print('pandas read csv:',data)
        else:
            data: DataFrame  = PandasTools.LoadSDF(temp_file.name, removeHs=False) # type: ignore
        return data

def get_task_type(df, target_cols:list[str]):
    try:
        if len(target_cols) > 1:
            if df[target_cols].nunique().values[0] > 2:
                return 'multilabel_regression'
            elif df[target_cols].nunique().values[0] == 2:
                return 'multilabel_classification'
            else:
                return 'unknown'
            
        series = pd.to_numeric(df[target_cols[0]], errors='coerce')
        if (series % 1 == 0).all():
            if series.nunique() > 2:
                return 'multiclass'
            elif series.nunique() == 2:
                return 'classification'
        else:
            return 'regression'
    except Exception:
        raise ValueError('获取任务类型错误')

def run_check_multi(data_bytes:bytes, type:Literal['.csv','.sdf'], smiles_col:str="SMILES", target_cols:str|list[str]|None="TARGET", n_cores=4) -> dict[str, Any]:
    df = tmp_read_input(data_bytes, type)
    ## 检查smiles列
    if type == '.csv':
        with Pool(processes=n_cores) as pool: 
            df['check_smiles_reasonable'] = pool.map(check_smiles, df[smiles_col])
        false_smiles_indexes = df[~df['check_smiles_reasonable']].index.tolist()
    else:
        df['check_smiles_reasonable'] = True
        false_smiles_indexes = []
    error_smiles_rows = df.iloc[false_smiles_indexes].to_dict(orient='records')

    # 检查targets列
    if target_cols:
        if isinstance(target_cols, str):
            target_cols = [col.strip() for col in target_cols.split(',')]
        if len(target_cols) == 1:
            df['check_target_reasonable'] = check_elements_can_convert_to_float(df, target_cols)
        elif len(target_cols) > 1:
            df['check_target_reasonable'] = check_elements_can_convert_to_float(df, target_cols).all(axis=1)

        false_target_indexes = df[~df['check_target_reasonable']].index.tolist() 

        new_df = df[(df['check_smiles_reasonable']) & (df['check_target_reasonable'])]
        
        error_target_rows = df.iloc[false_target_indexes].to_dict(orient='records')
        error_rows=[*error_smiles_rows, *error_target_rows]
    else:
        new_df = df[(df['check_smiles_reasonable'])]
        error_rows=[*error_smiles_rows]

    for col in ['check_smiles_reasonable', 'check_target_reasonable']:
        if col in new_df.columns:
            new_df.drop(columns=[col], inplace=True)
    return {
        'data_df':new_df,
        'data_type':type,
        "error_rows":error_rows,
    }

def save_upload_file(path:Path, content:bytes) -> list[str]:
    print('save path:',path.as_posix())
    with open(path.as_posix(), "wb") as f:
        f.write(content)
    # 提取列名
    columns:list[str] = []
    file_extension: str = path.suffix
    if file_extension == ".csv":
        df = pd.read_csv(BytesIO(content), encoding="utf-8", nrows=1)
        columns = list(df.columns)
    else:
        file_content_str = content.decode("utf-8")
        lines = file_content_str.splitlines()
        for line in lines:
            if line.strip() == "$$$$":
                break
            if "<" in line and ">" in line:
                match = re.search("<(.*?)>", line)
                if match:
                    columns.append(match.group(1))
    return columns

def read_input(file_path:Path) -> DataFrame:
        if file_path.suffix=='.csv':
            data = pd.read_csv(file_path)
        elif file_path.suffix=='.sdf':
            data = PandasTools.LoadSDF(file_path, removeHs=False) # type: ignore
        else:
            raise ValueError('Unknown file format: {}'.format(file_path))
        return data

def save_df_to_file(new_df:DataFrame, file_type:str, out_path:Path):
    if file_type == '.csv':
        new_df.to_csv(out_path, index=False)
    elif file_type == '.sdf':
        PandasTools.WriteSDF(new_df, out_path, properties=list(new_df.columns), idName='ID')
    else:
        raise ValueError('Unknown datatype: {}'.format(file_type))

if __name__ == '__main__':
    data_path = '/vepfs/fs_users/cuiyaning/data/test/0517/combined.csv'

    # # 测试run_check_single函数的运行时间
    # start_time = timeit.default_timer()
    # a, b = run_check_single(data_path)
    # end_time = timeit.default_timer()
    # print(a, b)
    # print(f"Execution time for run_check_single function: {end_time - start_time} seconds")

    # #cProfile.run('run_check_single(data_path)')
    # # 测试多核版本的run_check_multi函数的运行时间
    # start_time = timeit.default_timer()
    # run_check_multi(data_path)
    # end_time = timeit.default_timer()
    # print(f"Execution time for multi-core run_check_multi function: {end_time - start_time} seconds")
    # #cProfile.run('run_check_multi(data_path)')

    # # 测试多核版本的run_check_multi函数的运行时间
    # start_time = timeit.default_timer()
    # a, b, new_df, datatype = run_check_multi(data_path)
    # end_time = timeit.default_timer()
    # print(a, b, new_df)
    # print(f"Execution time for multi-core run_check_multi function: {end_time - start_time} seconds")
    # save_new_df(new_df, datatype, data_path)

