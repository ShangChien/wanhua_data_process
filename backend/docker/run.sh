#!/bin/bash
# 同步时间
apt-get update && apt-get install -y tzdata
# 设置时区为北京时间
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo "Asia/Shanghai" > /etc/timezone

### 启动 MongoDB
# 获取 DEPLOY_MODE 环境变量，如果未设置则默认为 prod
DEPLOY_MODE=${DEPLOY_MODE:-"dev"}

# 根据 DEPLOY_MODE 设置 port
if [ "$DEPLOY_MODE" = "dev" ]; then
    call_port=5001
else
    call_port=5002
fi

# 激活 Python 虚拟环境并运行应用程序
conda init
source ~/.bashrc
uvicorn service.main:app --host 0.0.0.0 --port "$call_port"

