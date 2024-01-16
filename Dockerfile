FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ARG FACEFUSION_VERSION=faceapi
ENV GRADIO_SERVER_NAME=0.0.0.0

WORKDIR /facefusion

RUN apt-get update
RUN apt-get install python3.10 -y
RUN apt-get install python-is-python3 -y
RUN apt-get install pip -y
RUN apt-get install git -y
RUN apt-get install curl -y
RUN apt-get install ffmpeg -y

RUN git clone https://github.com/drgarbage/facefusion.git --branch ${FACEFUSION_VERSION} --single-branch .
RUN python install.py --torch cuda --onnxruntime cuda --skip-venv

RUN cd /usr/local/lib/python3.10/dist-packages/torch/lib && ln -s libnvrtc-672ee683.so.11.2 libnvrtc.so

RUN mkdir /facefusion/public
RUN chmod 777 /facefusion/public