import uvicorn
from fastapi import FastAPI, Response, status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from urllib.parse import urlparse, parse_qs

from src.youtube import api as yt_api
from src.youtube import downloader
app = FastAPI()

AVAILABLE_PLATFORMS = ("youtube", )
class Item(BaseModel):
    url: str


@app.get("/health")
async def health_check():
    return {"status" : "ok"}

@app.get("/download/{platform}/{key}")
async def get_file(platform: str, key: str, response: Response):
    if platform not in AVAILABLE_PLATFORMS:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {}

    if platform == "youtube":
        result = yt_api.get_output_path(key)
        return FileResponse(result['output_path'], filename=result['title'], media_type="video/*")

@app.post("/download")
async def download(item: Item, background_tasks: BackgroundTasks, response: Response):
    parsed_url = urlparse(item.url)
    if parsed_url.netloc == 'www.youtube.com':
        params = parse_qs(parsed_url.query).get('v', [])
        if not params:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {}
        background_tasks.add_task(downloader.download, item.url)
        return {"status_url" : f"/status/youtube/{params[0]}"}
    return {}

@app.get("/status/{platform}/{key}")
async def get_status(platform: str, key: str, response: Response):
    if platform not in AVAILABLE_PLATFORMS:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {}

    if platform == "youtube":
        result = yt_api.get_status(key)
        if result['status_code'] == 'DONE':
            return RedirectResponse(f"/download/{platform}/{key}", status_code=status.HTTP_303_SEE_OTHER)
        return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
