from typing import Any
from dataclasses import dataclass
import jwt
import httpx
from pydantic import BaseModel
import logging
from bohrium_open_sdk import OpenSDK

logger =logging.getLogger("app")

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnn3jPyW81YqSjSLWBkdE
ZzurZ5gimj6Db693bO0WvhMPABpYdOTeAU1mnQh2ep4H7zoUdz4PKARh/p5Meh6l
ejtbyliptvW9WXg5LoquIzPyTe5/2W9GoTrzDHMdM89Gc2dn16TbsKU5z3lROlBP
Q2v7UjQCbs8VpSogb44kOn0cx/MV2+VBfJzFWkJnaXxc101YUteJytJRMli0Wqev
nYqzCgrtbdvqVF/8hqETZOIWdWlhRDASdYw3R08rChcMJ9ucZL/VUM+aKu+feekQ
UZ6Bi6CeZjgqBoiwccApVR88WbyVXWR/3IFvJb0ndoSdH85klpp25yVAHTdSIDZP
lQIDAQAB
-----END PUBLIC KEY-----
""".strip()

class UserExtend(BaseModel):
	updates:int|Any 		# 0
	robot:int|Any			# 1,
	bohrLang: str|Any 		#'zh-cn',
	squareLang: str|Any		#'zh-cn',
	showRobotTips:bool|Any	# False,

class UserInBohr(BaseModel):
	userId: int|Any 		#	20338,
	email: str|Any 			#	estss@163.com',
	phone: str|Any			#	'',
	projectCount: int|Any 	#	3,
	group: str|Any			#	'',
	orgName	: str|Any		#	'',
	userName: str|Any		#	'SayHi',
	oversea: int|Any		#	1,
	phoneVerify: int|Any	#	2,
	isBindWechat:bool|Any	# 	False,
	isSetPwd: bool|Any		#	True,
	weChatNickname: str|Any	#	'',
	weChatQrCode: str|Any	#	'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=gQFC8jwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyRmdPMmRTYXdmREYxQzg3TE5DYzQAAgSIuodmAwQAjScA',
	gitLoginName: str|Any	#	'',
	areaCode: int|Any		#	0,
	followed: bool|Any		#	False,
	showDataset: bool|Any	#	True,
	userExtId: str|Any		#	'bohr92a404',
	avatarUrl: str|Any 		#	'https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/article/20332/405615385095449fb2d8494381285c8c/bec17506-0074-4bd5-85ca-8fb5cf830a1d.png',
	level: int|Any 			#	1,
	showDatasetV2: bool|Any #	True,
	userType: str|Any		#	'user',
	orgVerified: bool|Any	#	 False,
	userNo: str|Any			#	'sbtopyob'
	extend:UserExtend|Any

def is_valid_bohr_token(token:str) -> Any | None:
	public_key = PUBLIC_KEY
	try:
		return jwt.decode(
			jwt=token,
			key=public_key,
			algorithms=["RS256"],
		)
	except Exception as e:
		logger.error(f'token:{token} is vaild:{e}')
		pass


async def get_bohr_user_info_by_token(token) -> None | UserInBohr:
	try:
		headers = {"Authorization": f"Bearer {token}"}
		response = httpx.get('https://bohrium.dp.tech/brm/v1/account/info', headers=headers)
		response.raise_for_status()
		res = response.json()
		if str(res["code"]) != "0":
			raise Exception(f"error code return : {res}")
		user_info = UserInBohr.model_validate(res['data'])
		return user_info
	except Exception as e:
		logger.error(f'fail to get bohrium user_info -> token: {token}; {e}')
		pass


@dataclass
class UserCookie:
	user_id:str
	name:str
	org_id:int

def get_bohr_user_info_oauth(access_key:str,app_key:str) -> UserCookie | None:
	try:
		client=OpenSDK(access_key=access_key,app_key=app_key)
		user_info = client.user.get_info()
		logger.info(f'进行验证{user_info}')
		if user_info and (user_info.get('code',None) == 0) and user_info.get('data',None):
			return UserCookie(**user_info['data'])
		
		logger.error(f'fail to get bohrium user_info -> access_key:{access_key}; app_key:{app_key}')
	except Exception as e:
		logger.error(f'fail to get bohrium user_info -> access_key:{access_key}; app_key:{app_key}. {e}')
		pass