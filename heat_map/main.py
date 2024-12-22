from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import config

app = FastAPI()

@app.get("/heat-map", response_class=HTMLResponse)
async def get_map():
    map_file = config.MAP_SAVE_PATH

    # 读取HTML文件并返回
    with open(map_file, "r", encoding="utf-8") as f:
        map_html = f.read()

    # 删除临时文件
    # os.remove(map_file)

    return HTMLResponse(content=map_html)