import sys, uvicorn
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from endpoints import auth, todo

app = FastAPI(title="FastAPI Web Server", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health", description="Health Checker", tags=['Health'])
async def check_health():
    return "Up and Running!"

app.include_router(auth.router, prefix='/auth', tags=['Authentication APIs'])
app.include_router(todo.router, tags=['Todo  APIs'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


