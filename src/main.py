from fastapi import FastAPI
from pages.router import router as page_router
from game.games import router as game_router
from fastapi.staticfiles import StaticFiles
import uvicorn



app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(page_router)
app.include_router(game_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8000,  reload=True,)