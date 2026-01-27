# # 使用Ubuntu 22.04作为基础镜像
# FROM informaticsmatters/rdkit-python3-debian:Release_2024_03

# # 设置环境变量，避免交互式配置tzdata
# ENV DEBIAN_FRONTEND=noninteractive
# ENV TZ=Asia/Shanghai

# # 更新apt源并安装必要的系统工具、库以及Python相关组件
# RUN apt-get update && \
#     apt-get install -y \
#         build-essential \
#         libpng-dev \
#         libopenbabel-dev \
#         cmake \
#         zlib1g-dev \
#         libboost-all-dev \
#         libxrender1 \
#         libxext6 \
#         libxft2 \
#         libfreetype6 \
#         libsm6 \
#         libice6 \
#         swig \
#         ntpdate \
#         wget \
#         gcc \
#         g++ \
#         tzdata \
#         mongodb-org \
#         software-properties-common && \
#     add-apt-repository ppa:deadsnakes/ppa && \
#     apt-get update && \
#     apt-get install -y python3.10 python3.10-dev && \
#     rm -rf /var/lib/apt/lists/*

# # 设置Python 3.10为默认Python版本（可选步骤）
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# # 同步市区时间
# RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# RUN echo "Asia/Shanghai" > /etc/timezone

# # 恢复交互式配置
# ENV DEBIAN_FRONTEND=dialog

# # 设置工作目录
# WORKDIR /

# # 将当前目录下的所有文件复制到容器的/app目录中
# COPY . /app

# # 使用Python 3.10安装项目依赖
# RUN cd /app && pip3.10 install --no-cache-dir -r requirements.txt

# # 容器启动时执行的命令，首先同步时间，然后运行应用程序
# CMD ntpdate pool.ntp.org && python3.10 -m app.main

# 使用官方的 Ubuntu 镜像作为基础镜像
FROM ubuntu:20.04

# 设置环境变量，避免交互式配置tzdata
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 更新包列表并安装必要的软件
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    libpng-dev \
    libopenbabel-dev \
    cmake \
    zlib1g-dev \
    libboost-all-dev \
    libxrender1 \
    libxext6 \
    libxft2 \
    libfreetype6 \
    libsm6 \
    libice6 \
    swig \
    chrony \
    wget \
    gcc \
    g++ \
    tzdata \
    gnupg

# 安装 Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip

# 安装 MongoDB 7.0
RUN wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org

# 创建 MongoDB 数据目录
RUN mkdir -p /data/db

# 暴露 MongoDB 默认端口
EXPOSE 27017

# 同步市区时间
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone

# 恢复交互式配置
ENV DEBIAN_FRONTEND=dialog

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器的/app目录中
COPY . /app

# 创建并激活 Python 虚拟环境，安装项目依赖
RUN python3.10 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# 验证安装版本
RUN python3.10 --version && mongod --version

# 添加启动脚本
RUN chmod +x /app/run.sh

# 容器启动时执行的命令，首先同步时间，然后运行应用程序
CMD ["/app/run.sh"]
