#!/bin/bash

# 设置错误处理
set -e

# 读取配置文件中的用户名、密码、镜像路径、组织域名和仓库名称
CONFIG_FILE="./.env.docker.json"

# 检查文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "配置文件 $CONFIG_FILE 不存在"
    exit 1
fi

# 读取用户名和密码
USERNAME=$(jq -r '.username' $CONFIG_FILE)
PASSWORD=$(jq -r '.password' $CONFIG_FILE)
IMAGE_PATH=$(jq -r '.image_path' $CONFIG_FILE)
ORG_DOMAIN=$(jq -r '.org_domain' $CONFIG_FILE)
REPO_NAME=$(jq -r '.repo_name' $CONFIG_FILE)

# 打印日志信息
echo "Username: $USERNAME"
echo "Image Path: $IMAGE_PATH"
echo "Org Domain: $ORG_DOMAIN"
echo "Repo Name: $REPO_NAME"

# 登录docker
echo $PASSWORD | docker login $ORG_DOMAIN --username $USERNAME --password-stdin

# 检查登录是否成功
if [ $? -ne 0 ]; then
    echo "Docker login failed"
    exit 1
fi

# 拉取 Docker 镜像
docker pull $IMAGE_PATH

# 停止并删除旧的容器
docker rm -f $REPO_NAME || true

# 运行新的容器
docker run -d -p 5000:5000 --name $REPO_NAME $IMAGE_PATH tail -f /dev/null
# docker run --name uniqsar -v /vepfs/fs_users/chensq/project/uniqsar:/workspace/data  -p 9526:9526  registry.dp.tech/dplc/uniqsar:latest-pytorch1.12.1-cuda11.6-rdma
# 将models和files 存放在/workspace/fastapi/data下
# cp /workspace/data/uni-qsra/back-end/inner_service/* ./ -r

# 检查容器是否启动成功
if [ $? -eq 0 ]; then
    echo "Container $REPO_NAME started successfully"
else
    echo "Failed to start container $REPO_NAME"
    exit 1
fi