#!/bin/bash

### mongoDB
#   
#   (dbname)            qsarDB
#   (root)              user:admin, pwd:qsar9527-admin
#   (readWrite)         user:qsar_user, pwd:qsar9527
#   (start)             mongod --config /etc/mongod.conf --fork
#   (stop)              pkill mongod
#   (shell connect)     mongosh --username admin --password *** --authenticationDatabase admin
#   (backup)            mongodump --db qsarDB --out /path/to/backup/directory --oplog
#   (restore)           mongorestore --db qsarDB /path/to/backup/directory/qsarDB --oplogReplay

### mongod.conf
# for documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/

# # Where and how to store data.
# storage:
#   dbPath: /vepfs/fs_users/chensq/project/data_uniqsar/db/mongodb
# #  engine:
# #  wiredTiger:

# # where to write logging data.
# systemLog:
#   destination: file
#   logAppend: true
#   path: /vepfs/fs_users/chensq/project/data_uniqsar/db/mongod.log

# # network interfaces
# net:
#   port: 27017
#   bindIp: 127.0.0.1


# # how the process runs
# processManagement:
#   timeZoneInfo: /usr/share/zoneinfo

# security:
#   authorization: enabled

# #operationProfiling:

# #replication:

# #sharding:

# ## Enterprise-Only Options:

# #auditLog:

# 同步时间
chronyd -q "server pool.ntp.org iburst"

### 启动 MongoDB
# 获取 DEPLOY_MODE 环境变量，如果未设置则默认为 prod
DEPLOY_MODE=${DEPLOY_MODE:-"dev"}

# 设置基础路径
BASE_PATH="/vepfs/fs_users/chensq/project/data_uniqsar/db"

# 根据 DEPLOY_MODE 设置 conf_path
if [ "$DEPLOY_MODE" = "dev" ]; then
    mongo_conf_path="${BASE_PATH}/mongod_dev.conf"
    call_port=7890
else
    mongo_conf_path="${BASE_PATH}/mongod.conf"
    call_port=7891
fi
mongod --config "$mongo_conf_path" --fork


# 激活 Python 虚拟环境并运行应用程序
source /app/.venv/bin/activate
pip3 install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port "$call_port"

