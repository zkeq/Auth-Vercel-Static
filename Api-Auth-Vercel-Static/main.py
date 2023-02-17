import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
import json
import uvicorn

app = FastAPI()

security = HTTPBasic()


def read_user_file():
    with open(os.path.join("Api-Auth-Vercel-Static", "user.json"), "r") as f:
        return json.loads(f.read())


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    current_password_bytes = credentials.password.encode("utf8")

    user_list = read_user_file()
    is_correct_username = False
    is_correct_password = False
    for user in user_list:
        correct_username_bytes = user["username"].encode("utf8")
        correct_password_bytes = user["password"].encode("utf8")
        #  secrets.compare_digest
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        is_correct_password = secrets.compare_digest(
            current_password_bytes, correct_password_bytes
        )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


# All routes
@app.get("/")
def read_root(_: str = Depends(get_current_username)):
    # 如果不存在
    if not os.path.exists("index.html"):
        return {
            "message": "index.html not found"
        }
    return FileResponse("index.html")


@app.get("/config.yaml")
def read_config():
    return {
        "msg": "Forbidden"
    }


# All routes
@app.get("/{path:path}")
def read_root(path: str, _: str = Depends(get_current_username)):
    # 如果是文件夹
    if os.path.isdir(path):
        path = os.path.join(path, "index.html")
    # 如果不存在
    if not os.path.exists(path):
        return {
            "message": f"{path} not found"
        }
    return FileResponse(path)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")