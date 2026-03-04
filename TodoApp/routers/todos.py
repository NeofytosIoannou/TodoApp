from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from starlette import status
from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user
from ..config import settings
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def is_admin(user: dict) -> bool:
    return (user.get('user_role') or '').lower() == 'admin'


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    owner_id: int | None = Field(default=None, gt=0)


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key=settings.cookie_name)
    return redirect_response


### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request)
        if user is None:
            return redirect_to_login()
        if is_admin(user):
            todos = db.query(Todos).all()
        else:
            todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()


@router.get('/add-todo-page')
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request)

        if user is None:
            return redirect_to_login()

        assignable_users = []
        if is_admin(user):
            assignable_users = db.query(Users).filter(Users.id != user.get('id')).order_by(Users.username).all()

        return templates.TemplateResponse(
            "add-todo.html",
            {"request": request, "user": user, "assignable_users": assignable_users}
        )

    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request)

        if user is None:
            return redirect_to_login()

        todo_query = db.query(Todos).filter(Todos.id == todo_id)
        if not is_admin(user):
            todo_query = todo_query.filter(Todos.owner_id == user.get('id'))
        todo = todo_query.first()

        if todo is None:
            return redirect_to_login()

        assignable_users = []
        if is_admin(user):
            assignable_users = db.query(Users).filter(Users.id != user.get('id')).order_by(Users.username).all()

        return templates.TemplateResponse(
            "edit-todo.html",
            {"request": request, "todo": todo, "user": user, "assignable_users": assignable_users}
        )

    except:
        return redirect_to_login()



### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
@router.get("/todo/{todo_id}/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_query = db.query(Todos).filter(Todos.id == todo_id)
    if not is_admin(user):
        todo_query = todo_query.filter(Todos.owner_id == user.get('id'))
    todo_model = todo_query.first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
@router.post("/todo/", status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    owner_id = user.get('id')
    if todo_request.owner_id is not None:
        if not is_admin(user):
            raise HTTPException(status_code=403, detail='Only admins can assign todos to other users.')

        existing_user = db.query(Users).filter(Users.id == todo_request.owner_id).first()
        if existing_user is None:
            raise HTTPException(status_code=404, detail='User not found.')
        owner_id = todo_request.owner_id

    todo_data = todo_request.model_dump(exclude={'owner_id'})
    todo_model = Todos(**todo_data, owner_id=owner_id)

    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.put("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_query = db.query(Todos).filter(Todos.id == todo_id)
    if not is_admin(user):
        todo_query = todo_query.filter(Todos.owner_id == user.get('id'))
    todo_model = todo_query.first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    if todo_request.owner_id is not None:
        if not is_admin(user):
            raise HTTPException(status_code=403, detail='Only admins can reassign todos.')

        existing_user = db.query(Users).filter(Users.id == todo_request.owner_id).first()
        if existing_user is None:
            raise HTTPException(status_code=404, detail='User not found.')
        todo_model.owner_id = todo_request.owner_id

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_query = db.query(Todos).filter(Todos.id == todo_id)
    if not is_admin(user):
        todo_query = todo_query.filter(Todos.owner_id == user.get('id'))
    todo_model = todo_query.first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.delete(todo_model)

    db.commit()












