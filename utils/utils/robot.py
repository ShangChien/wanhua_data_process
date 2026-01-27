import asyncio
from typing import List, Dict, Optional, Tuple,Any
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
from rdkit import Chem

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_cid(cas: str, client:httpx.AsyncClient) -> int | None:
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/cids/JSON/"
        response = await client.get(url)
        response.raise_for_status()  # 若状态码非 200 会抛异常
        data = response.json()
        cids = data.get('IdentifierList', {}).get('CID', [])
        return int(cids[0]) if cids else None
    except Exception as e:
        raise e

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_by_cid(cid: int,client:httpx.AsyncClient) -> dict:
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
        response = await client.get(url)
        response.raise_for_status()  # 若状态码非 200 会抛异常
        data = response.json()
        return data
    except Exception as e:
        raise e


def find_dict_by_key_value(data, target_key, target_value):
    """
    在嵌套字典中查找符合特定key:value条件的字典
    
    参数:
        data: 要搜索的字典或列表
        target_key: 要匹配的键
        target_value: 要匹配的值
    
    返回:
        第一个匹配的字典，如果没有找到则返回None
    """
    if isinstance(data, dict):
        # 检查当前字典是否匹配
        if target_key in data and data[target_key] == target_value:
            return data
        # 递归检查字典的值
        for value in data.values():
            result = find_dict_by_key_value(value, target_key, target_value)
            if result is not None:
                return result
    elif isinstance(data, list):
        # 如果是列表，递归检查每个元素
        for item in data:
            result = find_dict_by_key_value(item, target_key, target_value)
            if result is not None:
                return result
    return None


def find_value_by_key(data, target_key):
    """
    在嵌套字典中查找指定key的第一个匹配值
    
    参数:
        data: 要搜索的字典或列表
        target_key: 要查找的键
    
    返回:
        第一个匹配的value，如果没有找到则返回None
    """
    if isinstance(data, dict):
        # 检查当前字典是否包含目标key
        if target_key in data:
            return data[target_key]
        # 递归检查字典的值
        for value in data.values():
            result = find_value_by_key(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        # 如果是列表，递归检查每个元素
        for item in data:
            result = find_value_by_key(item, target_key)
            if result is not None:
                return result
    return None


def get_fema(data:dict) -> int | None:
    fema_dict = find_dict_by_key_value(data, 'Name', 'FEMA Number')
    if fema_dict is not None:
        fema_value = fema_dict.get('Value', {}).get('StringWithMarkup', [{}])[0].get('String', '')
        return int(fema_value)
    return None

def get_iupac(data:dict) -> str | None:
    iupac_dict = find_dict_by_key_value(data, 'TOCHeading', 'IUPAC Name')
    if iupac_dict is not None:
        iupac_value = iupac_dict.get('Information', [{}])[0].get("Value",{}).get('StringWithMarkup', [{}])[0].get('String', '')
        return iupac_value
    return None

def get_smiles(data:dict) -> str | None:
    smiles_dict = find_dict_by_key_value(data, 'TOCHeading', 'SMILES')
    if smiles_dict is not None:
        smiles = smiles_dict.get('Information', [{}])[0].get("Value",{}).get('StringWithMarkup', [{}])[0].get('String', '')
        return Chem.CanonSmiles(smiles)
    return None


## odor/flavor label extraction utils
BASE = "https://www.thegoodscentscompany.com"

def extract_odor_and_flavor_labels(html: str) ->List[str]:
    """
    只从 datasheet 里的 <table class="cheminfo"> 中提取：
      - /odor/*.html 下面的标签
      - /flavor/*.html 下面的标签

    返回:
      labels
    """
    soup = BeautifulSoup(html, "lxml")

    labels_set = set()
    for a in soup.select('table.cheminfo td.radw5 a[href^="/odor/"]'):
        txt = a.get_text(strip=True)
        if txt:
            labels_set.add(txt.lower())


    for a in soup.select('table.cheminfo td.radw5 a[href^="/flavor/"]'):
        txt = a.get_text(strip=True)
        if txt:
            labels_set.add(txt.lower())

    odor_labels = sorted(labels_set)

    return odor_labels


async def fetch_datasheet_url_for_cas(
    client: httpx.AsyncClient, cas: str
) -> Optional[str]:
    """
    通过 CAS 号访问 /opl/{cas}.html，
    找到 “Back To Datasheet” 链接，返回 datasheet URL。
    """
    opl_url = f"{BASE}/opl/{cas}.html"

    r = await client.get(opl_url, timeout=20)
    if r.status_code != 200:
        print(f"[{cas}] opl page not found (status {r.status_code})")
        return None

    soup = BeautifulSoup(r.text, "lxml")
    datasheet_url = None
    for a in soup.find_all("a"):
        text = a.get_text(strip=True).lower()
        if "back to datasheet" in text:
            href = a.get("href")
            if href and isinstance(href, str):
                datasheet_url = urljoin(BASE, href)
            break

    if not datasheet_url:
        print(f"[{cas}] datasheet link not found on opl page")
    return datasheet_url

async def get_smiles_with_cas_from_odor(cas: str, client: httpx.AsyncClient) -> str:
    try:
        opl_url = f"{BASE}/opl/{cas}.html"

        r = await client.get(opl_url, timeout=20)
        if r.status_code != 200:
            print(f"[{cas}] opl page not found (status {r.status_code})")
            return ''

        soup = BeautifulSoup(r.text, "lxml")
        for div in soup.select("div.mrado5"):
            text = div.get_text(" ", strip=True)
            if text.startswith("SMILES"):
                span = div.find("span", class_="mrado1")
                if span:
                    smiles = span.get_text(strip=True)
                    return Chem.CanonSmiles(smiles)
        return ''
    except Exception as e:
        print(f"[{cas}] error: get_smiles_with_cas_from_odor {e}")
        return ''



async def fetch_labels_for_cas(
    client: httpx.AsyncClient, cas: str,
) -> Tuple[str, List[str]]:
    """
    主流程：
      1. 找 datasheet URL
      2. 抓 datasheet
      3. 提取 odor 和 flavor 标签
    """
    datasheet_url = await fetch_datasheet_url_for_cas(client, cas)
    if not datasheet_url:
        return cas, []
    
    r = await client.get(datasheet_url, timeout=30)
    if r.status_code != 200:
        print(f"[{cas}] datasheet fetch error (status {r.status_code})")
        return cas, []
    
    labels = extract_odor_and_flavor_labels(r.text)
    return cas, labels



async def get_dict_from_cas(cas:str,client:httpx.AsyncClient,sem:asyncio.Semaphore,error_list:list) -> Dict[str, Any]:
    data = {
            "cas":cas,
            "fema":None,
            "iupac":None,
            "smiles":None,
            "odor_labels":[],
            'source':'wanhua'
        }
    cid=None
    try:
        async with sem:
            try:
                cid = await get_cid(cas,client)
            except Exception as e:
                print(f"[{cas}] error: {e}")
                error_list.append(cas)

            if cid:
                try:
                    compound_data = await fetch_by_cid(cid, client)
                    data['fema'] = get_fema(compound_data)
                    data['iupac'] = get_iupac(compound_data)
                    data['smiles'] = get_smiles(compound_data)
                except Exception as e:
                    print(f"[{cas}] error: {e}")
                    error_list.append(cas)
                    
            
            
            if data['smiles'] is None:
                data['smiles'] = await get_smiles_with_cas_from_odor(cas,client)

            _, odor_labels = await fetch_labels_for_cas(client, cas)
            data['odor_labels'] = odor_labels
            return data
    except Exception as e:
        print(f"[{cas}] error: {e}")
        error_list.append(cas)
        return data

def merge_data(csv_path: str):
    import pandas as pd
    df =  pd.read_csv(csv_path)

    # 定义合并逻辑函数
    def merge_group(group):
        # smiles：优先选择包含手性或异构标识的
        smiles_with_stereo = group['smiles'].dropna().loc[
            group['smiles'].str.contains("@|/|\\\\", regex=True, na=False)
        ]
        smiles = smiles_with_stereo.iloc[0] if not smiles_with_stereo.empty else group['smiles'].dropna().iloc[0]

        # odor_labels：去重后用逗号连接
        odors = set()
        for o in group['odor_labels'].dropna():
            odors.update(map(str.strip, o.split(',')))
        odor_labels = ",".join(sorted(odors)) if odors else None

        # 其他字段：保留第一个非空值
        def first_nonempty(col):
            nonempty = group[col].dropna()
            if not nonempty.empty:
                return nonempty.iloc[0]
            return None

        return pd.Series({
            'smiles': smiles,
            'cas': group['cas'].iloc[0],
            'iupac': first_nonempty('iupac'),
            'fema': first_nonempty('fema'),
            'odor_labels': odor_labels,
            'odor_threshold': first_nonempty('odor_threshold'),
            'source': first_nonempty('source'),
            'IFRA_name': first_nonempty('IFRA_name'),
            'IFRA': first_nonempty('IFRA'),
        })

    # 分离 cas 为空与非空部分
    has_cas = df[df['cas'].notna()]
    no_cas = df[df['cas'].isna()]

    # 对非空 cas 进行分组合并
    merged_has_cas = (
        has_cas.groupby('cas', dropna=False, group_keys=False)
        .apply(lambda g: merge_group(g.reset_index(drop=True)))
        .reset_index(drop=True)
    )

    # 合并回所有数据
    merged_df = pd.concat([merged_has_cas, no_cas], ignore_index=True)

    return merged_df


async def main_use(cas_list: List[str]) -> list[dict]:
    semaphore = asyncio.Semaphore(10)
    headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        }
    error_list = []
    async with httpx.AsyncClient(headers=headers, http2=True) as client:
        tasks = [
            get_dict_from_cas(cas,client,semaphore,error_list)
            for cas in cas_list
        ]
        results = await asyncio.gather(*tasks)

    return results



if __name__ == "__main__":
    asyncio.run(main_use([]))
