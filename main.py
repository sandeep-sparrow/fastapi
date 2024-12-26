import sys, uvicorn
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, Request
# relative imports
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Web Server", version="1.0.1")
templates = Jinja2Templates(directory="TodoApp/templates")
app.mount("/static", StaticFiles(directory='TodoApp/static'), name='static')

@app.get("/")
def home_test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/health", description="Health Checker", tags=['Health'])
async def health_check():
    return { 'status': "Up and Running!" }
app.include_router(todos.router)
app.include_router(users.router, prefix='/user', tags=['User'])
app.include_router(admin.router, prefix='/admin/todo', tags=['Administration'])
app.include_router(auth.router, prefix='/auth', tags=['Authentication'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


