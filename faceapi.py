from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import uuid
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允許所有域名
    allow_credentials=True,
    allow_methods=[""], # 允許所有方法
    allow_headers=["*"], # 允許所有標頭
)

class SwapFaceRequest(BaseModel):
    type: str  # "image" or "video"
    source: str
    target: str

@app.get("/")
def info():
    return { "result": "Server Running" }

@app.post("/api/swapface")
def swap_face(request: SwapFaceRequest):
    # 檢查請求參數
    if request.type not in ["image", "video"]:
        raise HTTPException(status_code=400, detail="Invalid type specified")

    target_extension = os.path.splitext(request.target)[1]

    if not target_extension:
        raise HTTPException(status_code=400, detail="Invalid target file extension")

    # 生成唯一的輸出文件名
    output_file = f"output_{uuid.uuid4()}{target_extension}"
    output_path = os.path.join("D:\\04.Photos\\swap", output_file)

    try:
        # 指定虛擬環境中的 Python 解釋器
        python_executable = "venv/Scripts/python"  # 或者是 "venv/bin/python"，取決於您的操作系統

        # 構建並執行 CLI 命令
        command = [
            python_executable, "run.py",
            "--headless",
            "--source", request.source,
            "--target", request.target,
            "--output", output_path,
            "--execution-providers", "cuda",
            "--frame-processors", "face_swapper", "face_enhancer",
            "--face-mask-types", "occlusion",
            # 添加其他必要的 CLI 參數
        ]
        subprocess.run(command, check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"result": output_path}