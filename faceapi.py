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

class SwapFaceRequest(BaseModel):
    source: str  # URL for the source image
    target: str  # URL for the target image or video

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
def swap_face(request: SwapFaceRequest, req:Request):
    # 下載文件
    source_file = download_file(request.source, './tmp/')
    target_file = download_file(request.target, './tmp/')
    if not source_file or not target_file:
        raise HTTPException(status_code=400, detail="Error downloading files")

    target_extension = os.path.splitext(target_file)[1]
    output_file = f"{uuid.uuid4().hex}{target_extension}"
    output_path = os.path.join("./public/", output_file)
    print(output_path)

    try:
        python_executable = "venv/Scripts/python"  # 虛擬環境中的 Python 解釋器
        command = [
            python_executable, "run.py",
            "--headless",
            "--source", source_file,
            "--target", target_file,
            "--output", output_path,
            "--execution-providers", "cuda",
            "--frame-processors", "face_swapper", "face_enhancer",
            "--face-mask-types", "occlusion",
            # 添加其他必要的 CLI 參數
        ]
        subprocess.run(command, check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 刪除暫存文件
        os.remove(source_file)
        os.remove(target_file)

    # 回傳結果文件的 URL
    result_url = f"{req.base_url}{output_file}"
    return {"result": result_url}

app.mount("/", StaticFiles(directory="public"), name="public")