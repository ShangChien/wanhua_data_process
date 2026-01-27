# qsar_service
backend for qsar



## 火山后端：
- 接口： http://101.126.67.113:7890/docs
- worker目录：/vepfs/fs_users/chensq/project/qsar_service
- 启动命令：
```sh
cd /vepfs/fs_users/chensq/project/qsar_service
python -m  app.main
```
- 文件地址：
1. 原始文件地址："/vepfs/fs_users/chensq/project/data_uniqsar/files/raw_files" 
2. 校验通过的文件地址："/vepfs/fs_users/chensq/project/data_uniqsar/files/valid_files"
3. ARTIFACT_NAME = 'my_model'
4. EXPERIMENT_NAME = 'my_experiment'


## 密集计算docker容器
- 接口：http://101.126.67.113:5001/docs
- 镜像：dp-ve-registry-cn-beijing.cr.volces.com/dplc/uniqsar:7d0dcf1b
- 挂载目录：/vepfs/fs_users/chensq/project/qsar_service/docker/
- 启动命令：
```sh
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install mlflow==2.13.0
cd /vepfs/fs_users/chensq/project/qsar_service/docker/
python -m service.main
```
- 目录list:
1. MLRESULTS_DIR = '/vepfs/fs_users/chensq/project/data_uniqsar/mlruns'
2. FILES_DIR = "/vepfs/fs_users/chensq/project/data_uniqsar/files/valid_files"
3. ARTIFACT_NAME = 'my_model'
4. EXPERIMENT_NAME = 'my_experiment'

