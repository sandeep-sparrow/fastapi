import sys, uvicorn
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from endpoints import auth, todos, admin, users

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
app.include_router(todos.router, prefix='/todo', tags=['Todo'])

app.include_router(users.router, prefix='/user', tags=['User'])
app.include_router(admin.router, prefix='/admin/todo', tags=['Administration'])
app.include_router(auth.router, prefix='/auth', tags=['Authentication'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


