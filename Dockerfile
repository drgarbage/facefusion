# 第一階段：基本環境設置
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as base

WORKDIR /facefusion

# 安裝依賴
RUN apt-get update && \
    apt-get install python3.10 -y && \
    apt-get install python-is-python3 -y && \
    apt-get install pip -y && \
    apt-get install git -y && \
    apt-get install curl -y && \
    apt-get install ffmpeg -y

# 第二階段：使用第一階段建立的環境
FROM base as final

ARG FACEFUSION_VERSION=faceapi
ENV GRADIO_SERVER_NAME=0.0.0.0

WORKDIR /facefusion

# 從Git克隆代碼
RUN git clone https://github.com/drgarbage/facefusion.git --branch ${FACEFUSION_VERSION} --single-branch .
RUN python install.py --torch cuda --onnxruntime cuda --skip-venv

# 建立CUDA庫的符號鏈接
RUN cd /usr/local/lib/python3.10/dist-packages/torch/lib && ln -s libnvrtc-672ee683.so.11.2 libnvrtc.so

# 建立並設定public資料夾的權限
RUN mkdir /facefusion/public
RUN chmod 777 /facefusion/public