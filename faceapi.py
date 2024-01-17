from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import uuid
import os
import requests
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlparse, unquote

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允許所有域名
    allow_credentials=True,
    allow_methods=[""], # 允許所有方法
    allow_headers=["*"], # 允許所有標頭
)


def download_file(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    response = requests.get(url)
    if response.status_code == 200:
        # 解析 URL 以獲取副檔名
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(unquote(parsed_url.path))[1]

        # 使用 UUID 生成檔案名稱，並附加副檔名
        file_name = uuid.uuid4().hex + file_extension
        file_path = os.path.join(dest_folder, file_name)

        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    return None


@app.post("/api/swapface")
async def swap_face(req: Request):
    # 获取请求数据
    request_data = await req.json()

    # 下载文件
    source_file = download_file(request_data.get("source"), './tmp/')
    target_file = download_file(request_data.get("target"), './tmp/')
    if not source_file or not target_file:
        raise HTTPException(status_code=400, detail="Error downloading files")

    target_extension = os.path.splitext(target_file)[1]
    output_file = f"{uuid.uuid4().hex}{target_extension}"
    output_path = os.path.join("./public/", output_file)

    try:
        # python_executable = "venv/Scripts/python"  # 虚拟环境中的 Python 解释器
        python_executable = "python"
        command = [
            python_executable, "run.py",
            "--headless",
            "--source", source_file,
            "--target", target_file,
            "--output", output_path,
        ]

        # 所有可能的参数字段
        options = [
            "execution-providers", "execution-thread-count", "execution-queue-count", "max-memory",
            "face-analyser-order", "face-analyser-age", "face-analyser-gender", "face-detector-model",
            "face-detector-size", "face-detector-score", "face-selector-mode", "reference-face-position",
            "reference-face-distance", "reference-frame-number", "face-mask-types", "face-mask-blur",
            "face-mask-padding", "face-mask-regions", "trim-frame-start", "trim-frame-end",
            "temp-frame-format", "temp-frame-quality", "keep-temp", "output-image-quality",
            "output-video-encoder", "output-video-quality", "keep-fps", "skip-audio", "frame-processors",
            "face-debugger-items", "face-enhancer-model", "face-enhancer-blend", "face-swapper-model",
            "frame-enhancer-model", "frame-enhancer-blend"
        ]

        # 处理参数字段
        for option in options:
            value = request_data.get(option)
            if value is not None:
                if option in ["execution-providers","face-mask-types","face-mask-padding","face-mask-regions","frame-processors","face-debugger-items"]:
                    # 对于数组参数，将所有值组合成一个列表，并将整个列表作为参数值添加到命令列表中
                    command.append(f"--{option}")
                    command.extend(value)
                else:
                    command.extend([f"--{option}", str(value)])

        subprocess.run(command, check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 删除临时文件
        os.remove(source_file)
        os.remove(target_file)

    # 返回结果文件的 URL
    result_url = f"{req.base_url}{output_file}"
    return {"result": result_url}



app.mount("/", StaticFiles(directory="public"), name="public")