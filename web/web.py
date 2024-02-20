import os
import uvicorn
from fastapi import FastAPI, Request, Form, status, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from web3 import Web3
from blockchain import User

load_dotenv()

AUTH_CONTRACT_ADDR = os.getenv('AUTH_CONTRACT_ADDR')
STORAGE_CONTRACT_ADDR = os.getenv('STORAGE_CONTRACT_ADDR')
ganache_url = 'http://127.0.0.1:7545'
web3 = Web3(Web3.HTTPProvider(ganache_url))

app = FastAPI(
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost', 'http://127.0.0.1'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
def get_session(request: Request, call_next):
    if 'private_key' in request.session.keys():
        try:
            user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
            if user.get_my_role() == '':
                request.scope['path'] = '/user_error'
            elif request.url.path == '/login':
                request.scope['path'] = '/panel'
        except:
            if request.url.path != '/login_error':
                request.scope['path'] = '/login'
    else:
        if request.url.path != '/login_error':
            request.scope['path'] = '/login'
    response = call_next(request)
    return response


app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY'))

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name='login.html')


@app.get("/logout")
def logout(request: Request):
    request.session.pop('private_key')
    return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)


@app.get("/login_error", response_class=HTMLResponse)
def login_error_page(request: Request):
    request.session['private_key'] = ''
    request.session.pop('private_key')
    return templates.TemplateResponse(request=request, name='login_error.html')


@app.get("/user_error", response_class=HTMLResponse)
def login_error_page(request: Request):
    request.session['private_key'] = ''
    request.session.pop('private_key')
    return templates.TemplateResponse(request=request, name='user_error.html')


@app.post("/login", response_class=HTMLResponse)
def login_handler(request: Request, key=Form(...)):
    try:
        user = User(web3, key, AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
        request.session['private_key'] = key
        return RedirectResponse('/panel', status_code=status.HTTP_302_FOUND)
    except:
        return RedirectResponse('/login_error', status_code=status.HTTP_302_FOUND)


@app.get("/panel", response_class=HTMLResponse)
def panel_page(request: Request):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    context = {'directories': user.get_directories(), 'role': user.get_my_role()}
    return templates.TemplateResponse(request=request, name='panel.html', context=context)


@app.get("/panel/{directory_title}", response_class=HTMLResponse)
def panel_page(request: Request, directory_title):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    try:
        files = user.get_directory(directory_title)[1]
    except:
        return RedirectResponse("/panel", status_code=status.HTTP_302_FOUND)
    context = {'directories': user.get_directories(), 'files': files,
               'directory': directory_title, 'role': user.get_my_role()}
    return templates.TemplateResponse(request=request, name='panel.html', context=context)


@app.post("/directory")
def create_directory(request: Request, title=Form(...)):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    try:
        user.create_directory(title)
        return {'status': 'ok'}
    except:
        return {'status': 'error'}


@app.delete("/directory")
def delete_directory(request: Request, title=Form(...)):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    try:
        user.delete_directory(title)
        return {'status': 'ok'}
    except:
        return {'status': 'error'}


@app.post("/file")
def create_file(request: Request, title=Form(...), directory=Form(...), roles=Form(...), file: UploadFile = File(...)):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    try:
        roles = roles.split()
        user.create_file(title, directory, file.file, roles)
        return {'status': 'ok'}
    except ValueError as e:
        print(e)
        return {'status': e.args[0]['data']['reason']}
    except:
        return {'status': 'error'}


@app.delete("/file")
def delete_file(request: Request, title=Form(...), directory=Form(...)):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    try:
        user.delete_file(title, directory)
        return {'status': 'ok'}
    except:
        return {'status': 'error'}


@app.get("/file")
def get_file_url(request: Request, title, directory):
    user = User(web3, request.session['private_key'], AUTH_CONTRACT_ADDR, STORAGE_CONTRACT_ADDR)
    try:
        r = user.get_file_hash(title, directory)
        return {'status': 'ok', 'url': 'https://ipfs.io/ipfs/' + r}
    except ValueError as e:
        return {'status': 'Not enough permissions'}
    except:
        return {'status': 'error'}


if __name__ == "__main__":
    uvicorn.run(app=app, port=80)
