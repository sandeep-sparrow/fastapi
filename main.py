import sys, uvicorn
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
# relative imports
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Web Server", version="1.0.1")

@app.get("/health", description="Health Checker", tags=['Health'])
async def health_check():
    return { 'status': "Up and Running!" }
app.include_router(todos.router)
app.include_router(users.router, prefix='/user', tags=['User'])
app.include_router(admin.router, prefix='/admin/todo', tags=['Administration'])
app.include_router(auth.router, prefix='/auth', tags=['Authentication'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


